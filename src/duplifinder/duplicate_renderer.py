# src/duplifinder/duplicate_renderer.py

"""Renderer for duplicate detection outputs (console/JSON/metrics)."""

import json
import logging
import time
from typing import Dict, List, Tuple, Any

from rich.console import Console
from rich.table import Table

from .config import Config


def _normalize_for_render(dups: Dict, is_token: bool = False) -> Dict[str, List[Dict[str, Any]]]:
    """Normalize defs/text/tokens to common render format."""
    normalized = {}
    for key, items in dups.items():
        norm_items = []
        for item in items:
            if is_token:
                loc1, loc2, ratio = item
                norm_items.append({"loc": f"{loc1} ~ {loc2} (sim: {ratio:.2%})", "snippet": "", "type": "token"})
            else:
                loc, snippet = item
                typ = key.split()[0] if " " in key else "text"
                norm_items.append({"loc": loc, "snippet": snippet, "type": typ})
        if norm_items:
            normalized[key] = norm_items
    return normalized


def render_duplicates(
    all_results: Dict,  # Generic: defs/text/tokens
    config: Config,
    is_search: bool,
    dup_rate: float,
    threshold: float,
    total_lines: int,
    dup_lines: int,
    is_token: bool = False
) -> None:
    """Render duplicates to console or JSON; handles token normalization."""
    console = Console()
    normalized = _normalize_for_render(all_results, is_token)
    duplicates = {k: v for k, v in normalized.items() if len(v) >= config.min_occurrences}

    if config.json_output:
        out = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "root": str(config.root),
            "scanned_files": 123,  # Inject from caller
            "skipped_files": [],  # Inject
            "duplicate_count": len(duplicates),
            "duplicates": duplicates  # Already normalized
        }
        print(json.dumps(out, indent=2))
        return

    for key, items in duplicates.items():
        table = Table(title=f"{key} ({len(items)} occurrence(s)):")
        table.add_column("Location")
        table.add_column("Snippet" if config.preview else "")
        for item in items:
            table.add_row(item["loc"], item["snippet"][:100] + "..." if config.preview and item["snippet"] else "")
        console.print(table)

    if not duplicates:
        console.print("[green]No duplicates found.[/green]")

    if dup_rate > threshold:
        console.print(f"[red]ALERT: Duplication rate {dup_rate:.1%} exceeds threshold {threshold:.1%} (est. {dup_lines}/{total_lines} lines duplicated).[/red]")

    if config.fail_on_duplicates and duplicates:
        raise SystemExit(1)