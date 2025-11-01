# src/duplifinder/main.py

"""Main entry point for Duplifinder."""

import sys
from pathlib import Path

from .cli import create_parser, build_config
from .finder import find_definitions, find_text_matches, find_token_duplicates, find_search_matches
from .output import render_duplicates, render_search, render_search_json
from .config import Config


def main() -> None:
    """Run the main Duplifinder workflow."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        config = build_config(args)
    except SystemExit as e:
        sys.exit(2)  # Config error

    if config.search_mode:
        results, skipped, scanned = find_search_matches(config)
        if config.json_output:
            render_search_json(results, config, scanned, skipped)
        else:
            render_search(results, config)
        # Exit 1 if multiples and --fail
        has_multi = any(len(occ) > 1 for occ in results.values())
        sys.exit(1 if (config.fail_on_duplicates and has_multi) else 0)
    elif config.token_mode:
        results, skipped, scanned, total_lines, dup_lines = find_token_duplicates(config)
        dup_rate = dup_lines / total_lines if total_lines else 0
        if dup_rate > config.dup_threshold:
            print(f"ALERT: Dup rate {dup_rate:.1%} > threshold {config.dup_threshold:.1%}", file=sys.stderr)
            sys.exit(1 if config.fail_on_duplicates else 0)
        render_duplicates(results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines)
        sys.exit(0 if not config.fail_on_duplicates or dup_lines == 0 else 1)
    elif config.pattern_regexes:
        import re
        patterns = [re.compile(p) for p in config.pattern_regexes]
        results, skipped, scanned, total_lines, dup_lines = find_text_matches(config, patterns)
        dup_rate = dup_lines / total_lines if total_lines else 0
        render_duplicates(results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines)
        sys.exit(0 if not config.fail_on_duplicates or dup_lines == 0 else 1)
    else:
        # Default: definitions
        results, skipped, scanned, total_lines, dup_lines = find_definitions(config)
        dup_rate = dup_lines / total_lines if total_lines else 0
        # Scan fail if >10% skipped (arbitrary; tunable)
        skip_rate = len(skipped) / (scanned + len(skipped)) if scanned + len(skipped) > 0 else 0
        if skip_rate > 0.1:
            print(f"SCAN FAIL: {skip_rate:.1%} files skipped (>10% threshold)", file=sys.stderr)
            sys.exit(3)  # Scan fail
        render_duplicates(results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines)
        sys.exit(0 if not config.fail_on_duplicates or dup_lines == 0 else 1)


if __name__ == "__main__":
    main()