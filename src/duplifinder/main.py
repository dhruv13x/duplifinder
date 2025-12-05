# src/duplifinder/main.py

"""Main entry point for Duplifinder."""

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
from pydantic import ValidationError

from .cli import create_parser, build_config
from .finder import find_definitions, find_text_matches, find_token_duplicates, find_search_matches
from .output import render_duplicates, render_search, render_search_json
from .config import Config
from .utils import audit_log_event
from .banner import print_logo
from .exceptions import DuplifinderError, ConfigError


def flatten_definitions(results: Dict[str, Dict[str, List[Tuple[str, str]]]] ) -> Dict[str, List[Tuple[str, str]]]:
    """Flatten nested definitions to flat Dict[str, List[Tuple]]."""
    flat = {}
    for typ, name_locs in results.items():
        for name, items in name_locs.items():
            key = f"{typ} {name}"
            flat[key] = items
    return flat


def main() -> None:
    """Run the main Duplifinder workflow."""
    print_logo()
    parser = create_parser()
    args = parser.parse_args()

    try:
        try:
            config = build_config(args)
        except (ConfigError, ValidationError, SystemExit) as e:
            if isinstance(e, SystemExit):
                raise
            # If it's a ConfigError from build_config (which calls load_config_file), print nicely
            # If it's a ValidationError from Pydantic, print nicely
            error_msg = str(e)
            if isinstance(e, ValidationError):
                # Format Pydantic errors a bit nicer if possible, or just dump string
                # e.errors() gives list of dicts.
                msgs = []
                for err in e.errors():
                    msgs.append(f"- {err['loc'][0]}: {err['msg']}")
                error_msg = "\n".join(msgs)

            print(f"Configuration Error:\n{error_msg}", file=sys.stderr)
            sys.exit(2)

        workflow_start = time.perf_counter()  # Start timing post-config

        if config.search_mode:
            results, skipped, scanned = find_search_matches(config)
            duration_ms = (time.perf_counter() - workflow_start) * 1000
            if config.json_output:
                render_search_json(results, config, scanned, skipped)
            else:
                render_search(results, config)
            # Audit: Scan complete aggregate
            audit_log_event(config, "scan_completed", mode="search", scanned=scanned, skipped=len(skipped), duration_ms=duration_ms)
            # Exit 1 if multiples and --fail
            has_multi = any(len(occ) > 1 for occ in results.values())
            sys.exit(1 if (config.fail_on_duplicates and has_multi) else 0)
        elif config.token_mode:
            results, skipped, scanned, total_lines, dup_lines = find_token_duplicates(config)
            dup_rate = dup_lines / total_lines if total_lines else 0
            duration_ms = (time.perf_counter() - workflow_start) * 1000
            if dup_rate > config.dup_threshold:
                print(f"ALERT: Dup rate {dup_rate:.1%} > threshold {config.dup_threshold:.1%}", file=sys.stderr)
                sys.exit(1 if config.fail_on_duplicates else 0)
            # <-- MODIFIED: Added scanned and skipped arguments
            render_duplicates(results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines, scanned, skipped, is_token=True)
            # Audit: Scan complete aggregate
            audit_log_event(config, "scan_completed", mode="token", scanned=scanned, skipped=len(skipped), total_lines=total_lines, dup_lines=dup_lines, dup_rate=dup_rate, duration_ms=duration_ms)
            sys.exit(0 if not config.fail_on_duplicates or dup_lines == 0 else 1)
        elif config.pattern_regexes:
            import re
            patterns = [re.compile(p) for p in config.pattern_regexes]
            results, skipped, scanned, total_lines, dup_lines = find_text_matches(config, patterns)
            dup_rate = dup_lines / total_lines if total_lines else 0
            duration_ms = (time.perf_counter() - workflow_start) * 1000
            # <-- MODIFIED: Added scanned and skipped arguments
            render_duplicates(results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines, scanned, skipped)
            # Audit: Scan complete aggregate
            audit_log_event(config, "scan_completed", mode="text_pattern", scanned=scanned, skipped=len(skipped), total_lines=total_lines, dup_lines=dup_lines, dup_rate=dup_rate, duration_ms=duration_ms)
            sys.exit(0 if not config.fail_on_duplicates or dup_lines == 0 else 1)
        else:
            # Default: definitions
            results, skipped, scanned, total_lines, dup_lines = find_definitions(config)
            dup_rate = dup_lines / total_lines if total_lines else 0
            duration_ms = (time.perf_counter() - workflow_start) * 1000
            # Scan fail if >10% skipped
            skip_rate = len(skipped) / (scanned + len(skipped)) if scanned + len(skipped) > 0 else 0
            if skip_rate > 0.1:
                print(f"SCAN FAIL: {skip_rate:.1%} files skipped (>10% threshold)", file=sys.stderr)
                # Audit: Even on fail
                audit_log_event(config, "scan_completed", mode="definitions", scanned=scanned, skipped=len(skipped), total_lines=total_lines, dup_lines=dup_lines, dup_rate=dup_rate, skip_rate=skip_rate, duration_ms=duration_ms, status="failed_skip_threshold")
                sys.exit(3)  # Scan fail
            # Flatten for render
            flat_results = flatten_definitions(results)
            # <-- MODIFIED: Added scanned and skipped arguments
            # <-- FIXED: Changed total_models to total_lines
            render_duplicates(flat_results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines, scanned, skipped)
            # Audit: Scan complete aggregate
            audit_log_event(config, "scan_completed", mode="definitions", scanned=scanned, skipped=len(skipped), total_lines=total_lines, dup_lines=dup_lines, dup_rate=dup_rate, duration_ms=duration_ms)
            sys.exit(0 if not config.fail_on_duplicates or dup_lines == 0 else 1)

    except DuplifinderError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
