# duplifinder/src/duplifinder/duplifinder/cli.py

"""CLI argument parsing and configuration merging."""

import argparse
import logging
import pathlib
from typing import Dict, List, Set

from .config import Config, DEFAULT_IGNORES, load_config_file
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="Find duplicate Python definitions across a project.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "root", nargs="*", help="Root directory to scan or find arguments."
    )
    parser.add_argument("--config", help="Path to configuration file (.duplifinder.yaml).")
    parser.add_argument("--ignore", default="", help="Comma-separated directory names to ignore.")
    parser.add_argument(
        "--exclude-patterns", default="", help="Comma-separated glob patterns for files to exclude."
    )
    parser.add_argument(
        "--exclude-names", default="", help="Comma-separated regex patterns for definition names to exclude."
    )
    parser.add_argument("-f", "--find", nargs="*", help="Types and names to find (e.g., 'class Base').")
    parser.add_argument("--find-regex", nargs="*", help="Regex patterns for types and names (e.g., 'class UI.*Manager').")
    parser.add_argument("--pattern-regex", nargs="*", help="Regex patterns for duplicate code snippets.")
    parser.add_argument("--json", action="store_true", help="Output as JSON.")
    parser.add_argument("--fail", action="store_true", help="Exit 1 if duplicates found.")
    parser.add_argument("--min", type=int, default=2, help="Min occurrences to report as duplicate.")
    parser.add_argument("--verbose", action="store_true", help="Print detailed logs.")
    parser.add_argument("--parallel", action="store_true", help="Scan files in parallel.")
    parser.add_argument("--use-multiprocessing", action="store_true", help="Use multiprocessing instead of threading.")
    parser.add_argument("--max-workers", type=int, help="Max workers for parallel processing.")
    parser.add_argument("-p", "--preview", action="store_true", help="Show formatted preview of duplicates.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def build_config(args: argparse.Namespace, config_dict: Dict) -> Config:
    """Merge CLI args with config file, CLI takes precedence."""
    root_candidates = args.root or config_dict.get("root", ["."])
    root_str = root_candidates[0] if pathlib.Path(root_candidates[0]).is_dir() else "."
    extra = root_candidates[1:] if len(root_candidates) > 1 else []

    # Setup logging early
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    config = Config(
        root=pathlib.Path(root_str).resolve(),
        ignore_dirs=DEFAULT_IGNORES.union(
            {x.strip() for x in (args.ignore or config_dict.get("ignore", "")).split(",") if x.strip()}
        ),
        exclude_patterns={
            x.strip() for x in (args.exclude_patterns or config_dict.get("exclude_patterns", "")).split(",") if x.strip()
        },
        exclude_names={
            x.strip() for x in (args.exclude_names or config_dict.get("exclude_names", "")).split(",") if x.strip()
        },
        types_to_search=set(),
        filter_names=set(),
        filter_regexes=args.find_regex or config_dict.get("find_regex", []),
        pattern_regexes=args.pattern_regex or config_dict.get("pattern_regex", []),
        json_output=args.json or config_dict.get("json", False),
        fail_on_duplicates=args.fail or config_dict.get("fail", False),
        min_occurrences=args.min or config_dict.get("min", 2),
        verbose=args.verbose or config_dict.get("verbose", False),
        parallel=args.parallel or config_dict.get("parallel", False),
        use_multiprocessing=args.use_multiprocessing or config_dict.get("use_multiprocessing", False),
        max_workers=args.max_workers or config_dict.get("max_workers", None),
        preview=args.preview or config_dict.get("preview", False),
    )

    # Process find arguments
    find_args = (args.find or config_dict.get("find", [])) + extra
    for item in find_args:
        if item in {"class", "def", "async_def"}:  # Inline KNOWN_TYPES check
            config.types_to_search.add(item)
        else:
            config.filter_names.add(item)
    if not config.types_to_search:
        config.types_to_search = {"class", "def", "async_def"}

    return config


def validate_config(config: Config, parser: argparse.ArgumentParser) -> None:
    """Validate configuration and raise errors."""
    unknown_types = config.types_to_search - {"class", "def", "async_def"}
    if unknown_types:
        parser.error(f"Unsupported types: {', '.join(unknown_types)}. Supported: class, def, async_def")

    if config.pattern_regexes:
        import re
        for rgx in config.pattern_regexes:
            try:
                re.compile(rgx)
            except re.error as e:
                parser.error(f"Invalid regex in --pattern-regex '{rgx}': {e}")