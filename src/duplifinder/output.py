# src/duplifinder/output.py

"""Output rendering for JSON and console."""

import json
import time
from typing import Dict, List, Tuple

try:
    from rich import print as rprint
    from rich.syntax import Syntax
except ImportError:
    rprint = print
    Syntax = None

from .config import Config


def render_duplicates(duplicates: Dict, config: Config, is_text_mode: bool) -> None:
    """Render duplicates to console."""
    if not duplicates:
        rprint("[bold green]No duplicates found.[/]")
        return

    for key in sorted(duplicates.keys()):
        items = duplicates[key]
        rprint(f"[bold bright_magenta]{key}[/] defined [bold green]{len(items)}[/] time(s):")
        locs_for_files = [item if is_text_mode else item[0] for item in items]
        files = {loc.split(":")[0] for loc in locs_for_files}
        if len(files) == 1:
            rprint(f"  [yellow](all occurrences in {list(files)[0]})[/]")
        for item in items:
            loc = item if is_text_mode else item[0]
            snippet = "" if is_text_mode else item[1]
            rprint(f"  [cyan]-> {loc}[/]")
            if config.preview and snippet:
                if Syntax:
                    rprint(Syntax(snippet, "python", theme="monokai", line_numbers=False))
                else:
                    rprint(snippet)


def render_json(duplicates: Dict, config: Config, is_text_mode: bool, scanned: int, skipped: List[str]) -> None:
    """Render output as JSON."""
    dup_out = {}
    for key, items in duplicates.items():
        dup_out[key] = [
            {"loc": item if is_text_mode else item[0], "snippet": "" if is_text_mode else item[1], "type": key.split()[0]}
            for item in items
        ]
    out = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": str(config.root),
        "scanned_files": scanned,
        "skipped_files": skipped if config.verbose else len(skipped),
        "ignore_dirs": sorted(list(config.ignore_dirs)),
        "exclude_patterns": sorted(list(config.exclude_patterns)),
        "exclude_names": sorted(list(config.exclude_names)),
        "duplicate_count": len(duplicates),
        "duplicates": dup_out,
    }
    print(json.dumps(out, indent=2))