# src/duplifinder/main.py

"""Main entrypoint for Duplifinder."""

import re
import sys
from typing import Dict, List, Tuple

from . import cli, finder, output
from .config import Config


def compute_duplicates(config: Config, is_text_mode: bool) -> Tuple[Dict, List[str], int]:
    """Compute duplicates based on mode."""
    skipped = []
    scanned = 0
    duplicates = {}

    if is_text_mode:
        import re
        text_patterns = [re.compile(rgx) for rgx in config.pattern_regexes]
        all_matches, skipped, scanned = finder.find_text_matches(config, text_patterns)
        duplicates = {f"pattern match '{matched}'": sorted(locs) for matched, locs in all_matches.items() if len(locs) >= config.min_occurrences}
    else:
        all_defs, skipped, scanned = finder.find_definitions(config)
        duplicates = {}
        for t, defs in all_defs.items():
            for name, loc_snippets in defs.items():
                if len(loc_snippets) < config.min_occurrences:
                    continue
                patterns = [p.split(" ", 1)[1] if " " in p else p for p in config.filter_regexes if " " not in p or p.startswith(f"{t} ")]
                include = (not config.filter_names and not patterns) or name in config.filter_names or any(re.match(pat, name) for pat in patterns)
                if not include:
                    continue
                key = f"{t} {name}" if t != "class" else f"class {name}"
                duplicates[key] = sorted(loc_snippets, key=lambda x: x[0])

    return duplicates, skipped, scanned


def main() -> None:
    """Main CLI execution."""
    parser = cli.create_parser()
    args = parser.parse_args()
    config_dict = cli.load_config_file(args.config) if args.config else {}
    config = cli.build_config(args, config_dict)
    cli.validate_config(config, parser)

    is_text_mode = bool(config.pattern_regexes)
    duplicates, skipped, scanned = compute_duplicates(config, is_text_mode)

    if config.json_output:
        output.render_json(duplicates, config, is_text_mode, scanned, skipped)
    else:
        output.render_duplicates(duplicates, config, is_text_mode)

    if config.fail_on_duplicates and duplicates:
        sys.exit(1)


if __name__ == "__main__":
    main()