# src/duplifinder/search_renderer.py

"""Renderer for search mode outputs (singletons/multi-occurrences)."""

import json
import logging
import time
from typing import Dict, List, Tuple

from rich.console import Console

from .config import Config


def render_search(
    search_results: Dict[str, List[Tuple[str, str]]],
    config: Config
) -> None:
    """Render search results to console."""
    console = Console()
    for spec, occ in search_results.items():
        count = len(occ)
        if count == 0:
            console.print(f"[yellow]No occurrences found for {spec}.[/yellow]")
            continue
        if count == 1 and not config.fail_on_duplicates:
            console.print(f"[green]Verified singleton: {spec} at {occ[0][0]}.[/green]")
        else:
            console.print(f"[blue]{spec} found {count} time(s):[/blue]")
            for loc, snippet in occ:
                console.print(f"  -> {loc}")
                if config.preview and snippet:
                    console.print(f"     {snippet[:80]}...")

        if config.fail_on_duplicates and count > 1:
            logging.warning(f"Multiple occurrences ({count}) for {spec}; failing per config.")
            raise SystemExit(1)


def render_search_json(
    search_results: Dict[str, List[Tuple[str, str]]],
    config: Config,
    scanned: int,
    skipped: List[str]
) -> None:
    """Render search results as JSON."""
    out = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": str(config.root),
        "scanned_files": scanned,
        "skipped_files": skipped if config.verbose else len(skipped),
        "search_specs": config.search_specs,
        "search_results": {
            spec: {
                "count": len(occ),
                "is_singleton": len(occ) == 1,
                "occurrences": [{"loc": loc, "snippet": snippet} for loc, snippet in occ]
            }
            for spec, occ in search_results.items()
        },
    }
    print(json.dumps(out, indent=2))