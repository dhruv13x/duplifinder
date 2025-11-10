# 🗃️ Project Code Dump

**Generated:** 2025-11-10T18:42:32+00:00 UTC
**Version:** 10.0.0
**Git Branch:** main | **Commit:** 82f6bdf

---

## Table of Contents

1. [search_finder.py](#search-finder-py)
2. [processor_utils.py](#processor-utils-py)
3. [duplicate_renderer.py](#duplicate-renderer-py)
4. [finder.py](#finder-py)
5. [search_renderer.py](#search-renderer-py)
6. [config.py](#config-py)
7. [main.py](#main-py)
8. [output.py](#output-py)
9. [ast_processor.py](#ast-processor-py)
10. [processors.py](#processors-py)
11. [text_finder.py](#text-finder-py)
12. [ast_visitor.py](#ast-visitor-py)
13. [definition_finder.py](#definition-finder-py)
14. [text_processor.py](#text-processor-py)
15. [cli.py](#cli-py)
16. [token_finder.py](#token-finder-py)
17. [utils.py](#utils-py)
18. [token_processor.py](#token-processor-py)

---

## search_finder.py

<a id='search-finder-py'></a>

```python
# src/duplifinder/search_finder.py

"""Search finder for specific definition occurrences (no dup filtering)."""

import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from .config import Config
from .processors import process_file_ast
from .utils import discover_py_files, run_parallel, log_file_count


def _parse_search_specs(config: Config) -> Dict[str, set]:
    """Parse search specs into {type: set(names)}."""
    spec_map = {}
    for spec in config.search_specs:
        parts = spec.strip().split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"Invalid spec '{spec}': Expected 'type name'")
        typ, name = parts
        if typ not in {"class", "def", "async_def"}:
            raise ValueError(f"Invalid type '{typ}' in '{spec}': Must be class, def, or async_def")
        spec_map.setdefault(typ, set()).add(name)
    return spec_map


def find_search_matches(config: Config) -> Tuple[Dict[str, List[Tuple[str, str]]], List[str], int]:
    """Find all occurrences matching search specs; no dup filtering."""
    all_matches: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # spec -> list of (loc, snippet)
    skipped: List[str] = []
    scanned = 0

    spec_map = _parse_search_specs(config)

    py_files = discover_py_files(config)
    log_file_count(py_files, config, "search")

    for result in run_parallel(py_files, process_file_ast, config=config):
        defs, skipped_file, _ = result  # Ignore lines for search
        if isinstance(skipped_file, str):
            skipped.append(skipped_file)
            logging.debug(f"Skipped file: {skipped_file}")
        else:
            scanned += 1
            for t, name_locs in defs.items():
                if t in spec_map:
                    for name, items in name_locs.items():
                        if name in spec_map[t]:
                            spec_key = f"{t} {name}"
                            all_matches[spec_key].extend(items)  # All locs/snippets

    if config.verbose:
        logging.info(f"Searched {scanned} files, skipped {len(skipped)}, found {sum(len(occ) for occ in all_matches.values())} occurrences")

    return all_matches, skipped, scanned
```

---

## processor_utils.py

<a id='processor-utils-py'></a>

```python
# src/duplifinder/processor_utils.py

"""Shared utilities for processors (e.g., dup estimation)."""

from typing import List

from .config import Config


def estimate_dup_lines(items: List, is_text_like: bool, config: Config) -> int:
    """Estimate duplicated lines from items (occ -1 * avg block size)."""
    if not items:
        return 0
    occ = len(items)
    if occ < config.min_occurrences:
        return 0
    # For AST: use snippet lines if preview, else heuristic (avg 10 lines)
    if not is_text_like:
        avg_size = sum(len(s.split('\n')) if s else 10 for _, s in items) // occ
    else:
        # For text/token: heuristic per match (avg 1-5 lines)
        avg_size = 3
    return (occ - 1) * avg_size * len(items)  # Conservative: per-item dup contrib
```

---

## duplicate_renderer.py

<a id='duplicate-renderer-py'></a>

```python
# src/duplifinder/duplicate_renderer.py

"""Renderer for duplicate detection outputs (console/JSON/metrics)."""

import json
import logging
import time
from typing import Dict, List, Tuple, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

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
                if isinstance(item, str):
                    loc = item
                    snippet = ""
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
    scanned_files: int,
    skipped_files: List[str],
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
            "scanned_files": scanned_files,
            "skipped_files": skipped_files,
            "duplicate_count": len(duplicates),
            "duplicates": duplicates  # Already normalized
        }
        print(json.dumps(out, indent=2))
        return

    if config.preview:
        # PREVIEW MODE: Use list format with Syntax Highlighting
        for key, items in duplicates.items():
            # Print a colorful title for the definition
            console.print(f"\n[bold magenta]{key}[/bold magenta] defined [bold yellow]{len(items)} time(s):[/bold yellow]")
            for item in items:
                loc = item["loc"]
                snippet = item["snippet"]
                # Print the location
                console.print(f"  -> [cyan]{loc}[/cyan]")
                
                if snippet:
                    # Create a Syntax object for highlighting
                    # We use "python" as the lexer
                    # We use a theme (like "monokai") to get the background color
                    # We disable rich's line numbers because the snippet already has them
                    syntax = Syntax(
                        snippet,
                        "python",
                        theme="monokai",
                        line_numbers=False 
                    )
                    # Print the Syntax object inside the Panel
                    console.print(Panel(syntax, border_style="dim", padding=(0, 1)))
                   
    else:
     
        # NO-PREVIEW MODE: Use the new, *colorful* compact table format
        for key, items in duplicates.items():
            # Add color to the title
            title = f"[bold magenta]{key}[/bold magenta] ([bold yellow]{len(items)}[/bold yellow] occurrence(s)):"
            
            # Add color and style to the table
            table = Table(title=title, border_style="blue")
            
            # Add color to the header
            table.add_column("Location", style="cyan")
            
            for item in items:
                table.add_row(item["loc"])  # Add location
            console.print(table)
        
    if not duplicates:
        console.print("[green]No duplicates found.[/green]")

    if dup_rate > threshold:
        console.print(f"[red]ALERT: Duplication rate {dup_rate:.1%} exceeds threshold {threshold:.1%} (est. {dup_lines}/{total_lines} lines duplicated).[/red]")

    # Audit nudge: Optional console hint if enabled
    if config.audit_enabled:
        console.print(f"[dim green]Audit trail logged to {config.audit_log_path}[/dim green]")

    if config.fail_on_duplicates and duplicates:
        raise SystemExit(1)

```

---

## finder.py

<a id='finder-py'></a>

```python
# src/duplifinder/finder.py

"""Dispatcher for finder modes; import submodules for focused logic."""

from .definition_finder import find_definitions
from .text_finder import find_text_matches
from .token_finder import find_token_duplicates
from .search_finder import find_search_matches

__all__ = ["find_definitions", "find_text_matches", "find_token_duplicates", "find_search_matches"]
```

---

## search_renderer.py

<a id='search-renderer-py'></a>

```python
# src/duplifinder/search_renderer.py

"""Renderer for search mode outputs (singletons/multi-occurrences)."""

import json
import logging
import time
from typing import Dict, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

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

        # Print the main title
        title_color = "green" if count == 1 else "blue"
        count_color = "green" if count == 1 else "bold yellow"
        title_text = "Verified singleton" if count == 1 else f"found {count} time(s)"
        
        console.print(f"\n[{title_color}]{spec}[/{title_color}] {title_text}:")

        for loc, snippet in occ:
            # Print the location
            console.print(f"  -> [cyan]{loc}[/cyan]")
            
            # If -p is used, show the full, highlighted panel
            if config.preview and snippet:
                syntax = Syntax(
                    snippet,
                    "python",
                    theme="monokai",
                    line_numbers=False
                )
                console.print(Panel(syntax, border_style="dim", padding=(0, 1)))

        if config.fail_on_duplicates and count > 1:
            logging.warning(f"Multiple occurrences ({count}) for {spec}; failing per config.")
            # Note: This SystemExit will be caught by main.py
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

```

---

## config.py

<a id='config-py'></a>

```python
# src/duplifinder/config.py

"""Configuration management with Pydantic validation."""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Set

# MODIFIED: Import field_validator and ValidationInfo, remove validator
from pydantic import BaseModel, Field, field_validator, ValidationInfo
import yaml

DEFAULT_IGNORES = {".git", "__pycache__", ".venv", "venv", "build", "dist", "node_modules"}
KNOWN_TYPES = {"class", "def", "async_def"}


class Config(BaseModel):
    """Validated configuration model."""

    root: Path = Field(default_factory=lambda: Path("."), description="Scan root directory")
    ignore_dirs: Set[str] = Field(default_factory=lambda: DEFAULT_IGNORES.copy())
    exclude_patterns: Set[str] = Field(default_factory=set)
    exclude_names: Set[str] = Field(default_factory=set)  # Raw patterns; compiled in processors
    types_to_search: Set[str] = Field(default_factory=lambda: {"class", "def", "async_def"})
    filter_names: Set[str] = Field(default_factory=set)
    filter_regexes: List[str] = Field(default_factory=list)
    pattern_regexes: List[str] = Field(default_factory=list)
    search_specs: List[str] = Field(default_factory=list)
    search_mode: bool = False
    token_mode: bool = False
    similarity_threshold: float = Field(0.8, ge=0.0, le=1.0)
    dup_threshold: float = Field(0.1, ge=0.0, le=1.0)
    json_output: bool = False
    fail_on_duplicates: bool = False
    min_occurrences: int = Field(2, ge=1)
    verbose: bool = False
    parallel: bool = False
    use_multiprocessing: bool = False
    max_workers: int | None = Field(None, ge=1)
    preview: bool = False
    audit_enabled: bool = Field(False, description="Enable audit logging for file access trails")
    audit_log_path: Path = Field(
        default_factory=lambda: Path(".duplifinder_audit.jsonl"),
        description="Path for audit log output (JSONL format)"
    )
    respect_gitignore: bool = Field(True, description="Auto-respect .gitignore patterns for exclusions")

    # MODIFIED: Use @field_validator
    @field_validator("types_to_search")
    def validate_types(cls, v: Set[str]) -> Set[str]:
        invalid = v - KNOWN_TYPES
        if invalid:
            raise ValueError(f"Unsupported types: {', '.join(invalid)}. Supported: {', '.join(KNOWN_TYPES)}")
        return v

    # MODIFIED: Use @field_validator with mode='before' (for pre=True)
    @field_validator("filter_regexes", "pattern_regexes", "exclude_names", mode='before')
    def compile_regexes(cls, v: List[str]) -> List[str]:
        import re
        compiled = []
        for pat in v:
            try:
                re.compile(pat)
                compiled.append(pat)
            except re.error as e:
                raise ValueError(f"Invalid regex '{pat}': {e}")
        return compiled

    # MODIFIED: Use @field_validator with mode='before' (for pre=True)
    @field_validator("search_specs", mode='before')
    def validate_search_specs(cls, v: List[str]) -> List[str]:
        if not v:
            return v
        import re
        valid_types = KNOWN_TYPES
        for spec in v:
            parts = spec.strip().split(maxsplit=1)
            if len(parts) != 2:
                raise ValueError(f"Invalid search spec '{spec}': Must be 'type name'.")
            typ, name = parts
            if typ not in valid_types:
                raise ValueError(f"Invalid type '{typ}' in '{spec}': {', '.join(valid_types)}")
            if not name:
                raise ValueError(f"Empty name in '{spec}'.")
        return v

    # MODIFIED: Use @field_validator and ValidationInfo to access other field data
    @field_validator("audit_log_path")
    def validate_audit_path(cls, v: Path, info: ValidationInfo) -> Path:
        # Access 'values' dict via info.data
        if info.data.get("audit_enabled") and not isinstance(v, Path):
            v = Path(v)
        if info.data.get("audit_enabled") and v.exists() and not v.parent.is_dir():
            raise ValueError(f"Audit log path '{v}' parent directory does not exist")
        return v


def load_config_file(path: str | Path) -> Dict:
    """Load YAML config with error handling."""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        raise ValueError(f"Failed to load config '{path}': {e}")
```

---

## main.py

<a id='main-py'></a>

```python
# src/duplifinder/main.py

"""Main entry point for Duplifinder."""

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
from .cli import create_parser, build_config
from .finder import find_definitions, find_text_matches, find_token_duplicates, find_search_matches
from .output import render_duplicates, render_search, render_search_json
from .config import Config
from .utils import audit_log_event


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
    parser = create_parser()
    args = parser.parse_args()

    try:
        config = build_config(args)
    except SystemExit as e:
        sys.exit(2)  # Config error

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


if __name__ == "__main__":
    main()
```

---

## output.py

<a id='output-py'></a>

```python
# src/duplifinder/output.py

"""Re-exports for backward compatibility; use submodules for new code."""

from .duplicate_renderer import render_duplicates
from .search_renderer import render_search, render_search_json

__all__ = ["render_duplicates", "render_search", "render_search_json"]
```

---

## ast_processor.py

<a id='ast-processor-py'></a>

```python
# src/duplifinder/ast_processor.py

"""AST file processor for definition extraction."""

import fnmatch
import logging
import tokenize
import re  # For exclude_names
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import ast

from .ast_visitor import EnhancedDefinitionVisitor
from .config import Config
from .utils import audit_log_event


def process_file_ast(py_file: Path, config: Config) -> Tuple[Dict[str, Dict[str, List[Tuple[str, str]]]], str | None, int]:
    """Process a single Python file for definitions using AST; return total_lines."""
    str_py_file = str(py_file)
    if any(fnmatch.fnmatch(py_file.name, pat) for pat in config.exclude_patterns):
        if config.verbose:
            logging.info(f"Skipping {str_py_file}: matches exclude pattern")
        audit_log_event(config, "file_skipped", path=str_py_file, reason="exclude_pattern_match")
        return {}, str_py_file, 0

    total_lines = 0
    try:
        # Audit: Log open attempt
        audit_log_event(config, "file_opened", path=str_py_file, action="ast_open")
        # Encoding-aware open with fallback
        with tokenize.open(py_file) as fh:  # Handles BOM/encoding
            text = fh.read()
        bytes_read = len(text)
        total_lines = len(text.splitlines())
        audit_log_event(config, "file_parsed", path=str_py_file, action="ast_success", bytes_read=bytes_read, lines=total_lines)
        
        tree = ast.parse(text, filename=str_py_file)
        lines = text.splitlines() if config.preview else []
        visitor = EnhancedDefinitionVisitor(config.types_to_search)
        visitor.visit(tree)
        definitions: Dict[str, Dict[str, List[Tuple[str, str]]]] = {t: defaultdict(list) for t in config.types_to_search}
        for t, items in visitor.definitions.items():
            for name, lineno, end_lineno, _ in items:
                if any(re.match(pat, name) for pat in config.exclude_names):
                    continue
                loc = f"{str_py_file}:{lineno}"
                snippet = ""
                if config.preview and lines:
                    snippet_lines = lines[lineno - 1 : end_lineno]
                    if snippet_lines:
                        # Find minimum indent, ignoring empty lines
                        indent = min((len(line) - len(line.lstrip())) for line in snippet_lines if line.strip())
                        snippet_lines = [line[indent:] for line in snippet_lines]
                        snippet = "\n".join(f"{i + 1} {line}" for i, line in enumerate(snippet_lines))
                definitions[t][name].append((loc, snippet))
        return definitions, None, total_lines
    
    # FIXED: Moved UnicodeDecodeError BEFORE ValueError
    except UnicodeDecodeError as e:
        reason = f"encoding_error: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.warning(f"Skipping {str_py_file} due to encoding error: {e}; try --encoding flag in future")
        return {}, str_py_file, 0
    except (SyntaxError, ValueError) as e:
        reason = f"{type(e).__name__}: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.error(f"Skipping {str_py_file} due to parsing error: {reason}", exc_info=config.verbose)
        return {}, str_py_file, 0
    except Exception as e:
        reason = f"{type(e).__name__}: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.error(f"Skipping {str_py_file}: {reason}", exc_info=config.verbose)
        return {}, str_py_file, 0
```

---

## processors.py

<a id='processors-py'></a>

```python
# src/duplifinder/processors.py

"""Re-exports for backward compatibility; use submodules for new code."""

from .ast_processor import process_file_ast
from .text_processor import process_file_text
from .token_processor import process_file_tokens, tokenize_block
from .processor_utils import estimate_dup_lines

__all__ = ["process_file_ast", "process_file_text", "process_file_tokens", "tokenize_block", "estimate_dup_lines"]
```

---

## text_finder.py

<a id='text-finder-py'></a>

```python
# src/duplifinder/text_finder.py

"""Text pattern finder using regex matches."""

import logging
import re
from collections import defaultdict
from typing import Dict, List ,Tuple

from .config import Config
from .processors import process_file_text, estimate_dup_lines
from .utils import discover_py_files, run_parallel, log_file_count


def find_text_matches(config: Config, patterns: List[re.Pattern]) -> Tuple[Dict[str, List[str]], List[str], int, int, int]:
    """Find text matches across the project, optionally in parallel; return total_lines, dup_lines."""
    all_matches: Dict[str, List[str]] = defaultdict(list)
    skipped: List[str] = []
    scanned = 0
    total_lines = 0
    dup_lines = 0

    py_files = discover_py_files(config)
    log_file_count(py_files, config)

    for result in run_parallel(py_files, process_file_text, patterns, config=config):
        matches, skipped_file, file_lines = result
        if isinstance(skipped_file, str):
            skipped.append(skipped_file)
            logging.debug(f"Skipped file: {skipped_file}")
        else:
            scanned += 1
            total_lines += file_lines
            for matched, locs in matches.items():
                all_matches[matched].extend(locs)
                dup_lines += estimate_dup_lines(locs, True, config)

    if config.verbose:
        logging.info(f"Scanned {scanned} files, skipped {len(skipped)}, total lines: {total_lines}, estimated dup lines: {dup_lines}")

    return all_matches, skipped, scanned, total_lines, dup_lines
```

---

## ast_visitor.py

<a id='ast-visitor-py'></a>

```python
# src/duplifinder/ast_visitor.py

"""AST visitor for collecting Python definitions."""

import ast
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from .config import KNOWN_TYPES


class EnhancedDefinitionVisitor(ast.NodeVisitor):
    """AST visitor to collect definitions and method names within classes."""

    def __init__(self, types_to_search: Set[str]) -> None:
        self.definitions: Dict[str, List[Tuple[str, int, int, str]]] = defaultdict(list)
        self.types_to_search = types_to_search
        self.current_class = None  # Track class context for methods

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if "class" in self.types_to_search:
            end_lineno = node.end_lineno if node.end_lineno is not None else node.lineno
            self.definitions["class"].append((node.name, node.lineno, end_lineno, ""))
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._collect_function(node, "def")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._collect_function(node, "async_def")

    def _collect_function(self, node, typ: str) -> None:
        if typ not in self.types_to_search:
            return
        end_lineno = node.end_lineno if node.end_lineno is not None else node.lineno
        name = node.name
        if self.current_class:
            name = f"{self.current_class}.{name}"
        self.definitions[typ].append((name, node.lineno, end_lineno, ""))
        self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        # No additional collection here; handled in specific visit methods
        super().generic_visit(node)
```

---

## definition_finder.py

<a id='definition-finder-py'></a>

```python
# src/duplifinder/definition_finder.py

"""AST-based definition finder for classes, functions, and async functions."""

import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from .config import Config
from .processors import process_file_ast, estimate_dup_lines
from .utils import discover_py_files, run_parallel, log_file_count


def find_definitions(config: Config) -> Tuple[Dict[str, Dict[str, List[Tuple[str, str]]]], List[str], int, int, int]:
    """Find definitions across the project using AST, optionally in parallel; return total_lines, dup_lines."""
    all_definitions: Dict[str, Dict[str, List[Tuple[str, str]]]] = {t: defaultdict(list) for t in config.types_to_search}
    skipped: List[str] = []
    scanned = 0
    total_lines = 0
    dup_lines = 0

    py_files = discover_py_files(config)
    log_file_count(py_files, config)

    for result in run_parallel(py_files, process_file_ast, config=config):
        defs, skipped_file, file_lines = result
        if isinstance(skipped_file, str):
            skipped.append(skipped_file)
            logging.debug(f"Skipped file: {skipped_file}")
        else:
            scanned += 1
            total_lines += file_lines
            for t, name_locs in defs.items():
                for name, items in name_locs.items():
                    all_definitions[t][name].extend(items)
                    dup_lines += estimate_dup_lines(items, False, config)

    if config.verbose:
        logging.info(f"Scanned {scanned} files, skipped {len(skipped)}, total lines: {total_lines}, estimated dup lines: {dup_lines}")

    return all_definitions, skipped, scanned, total_lines, dup_lines
```

---

## text_processor.py

<a id='text-processor-py'></a>

```python
# src/duplifinder/text_processor.py

"""Text file processor for regex pattern matching."""

import fnmatch
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Tuple

from .config import Config
from .utils import audit_log_event


def process_file_text(py_file: Path, patterns: List[re.Pattern], config: Config) -> Tuple[Dict[str, List[str]], str | None, int]:
    """Process a single Python file for text patterns; return total_lines."""
    str_py_file = str(py_file)
    if any(fnmatch.fnmatch(py_file.name, pat) for pat in config.exclude_patterns):
        if config.verbose:
            logging.info(f"Skipping {str_py_file}: matches exclude pattern")
        audit_log_event(config, "file_skipped", path=str_py_file, reason="exclude_pattern_match")
        return {}, str_py_file, 0

    total_lines = 0
    try:
        # Audit: Log open attempt
        audit_log_event(config, "file_opened", path=str_py_file, action="text_open")
        # Encoding-aware open
        with open(py_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        bytes_read = sum(len(line) for line in lines)
        total_lines = len(lines)
        audit_log_event(config, "file_parsed", path=str_py_file, action="text_success", bytes_read=bytes_read, lines=total_lines)
        
        matches: Dict[str, List[str]] = defaultdict(list)
        for lineno, line in enumerate(lines, 1):
            for pat in patterns:
                if pat.search(line):
                    matches[pat.pattern].append(f"{str_py_file}:{lineno}")
        return matches, None, total_lines
    except UnicodeDecodeError as e:
        reason = f"encoding_error: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.warning(f"Skipping {str_py_file} due to encoding error: {e}")
        return {}, str_py_file, 0
    except Exception as e:
        reason = f"{type(e).__name__}: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.error(f"Skipping {str_py_file}: {reason}", exc_info=config.verbose)
        return {}, str_py_file, 0
```

---

## cli.py

<a id='cli-py'></a>

```python
# src/duplifinder/cli.py

"""CLI argument parsing and config building."""

import argparse
import logging
import pathlib
from typing import Dict

from .config import Config, load_config_file, DEFAULT_IGNORES
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="Find duplicate Python definitions across a project.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    # Positional: Scan roots
    parser.add_argument("root", nargs="*", help="Root directory to scan or find arguments.")
    
    # Config & Filtering Groups
    config_group = parser.add_argument_group("Configuration & Filtering")
    config_group.add_argument("--config", help="Path to configuration file (.duplifinder.yaml).")
    config_group.add_argument("--ignore", default="", help="Comma-separated directory names to ignore.")
    config_group.add_argument("--exclude-patterns", default="", help="Comma-separated glob patterns for files to exclude.")
    config_group.add_argument("--exclude-names", default="", help="Comma-separated regex patterns for definition names to exclude.")
    config_group.add_argument("--no-gitignore", action="store_true", help="Disable auto-respect of .gitignore patterns (default: respect).")
    
    # Scan Mode Groups
    scan_group = parser.add_argument_group("Scan Modes")
    scan_group.add_argument("-f", "--find", nargs="*", help="Types and names to find (e.g., 'class Base').")
    scan_group.add_argument("--find-regex", nargs="*", help="Regex patterns for types and names (e.g., 'class UI.*Manager').")
    scan_group.add_argument("--pattern-regex", nargs="*", help="Regex patterns for duplicate code snippets.")
    scan_group.add_argument("-s", "--search", nargs='+', help="Search all occurrences of specific definitions (e.g., 'class UIManager', 'def dashboard_menu'). Requires type and name.")
    scan_group.add_argument("--token-mode", action="store_true", help="Enable token-based duplication detection for non-definition code.")
    
    # Thresholds & Behavior
    behavior_group = parser.add_argument_group("Thresholds & Behavior")
    behavior_group.add_argument("--similarity-threshold", type=float, default=0.8, help="Similarity ratio threshold for token duplicates (0.0-1.0, default: 0.8).")
    behavior_group.add_argument("--dup-threshold", type=float, default=0.1, help="Duplication rate threshold for alerts (0.0-1.0, default: 0.1; warns if exceeded).")
    behavior_group.add_argument("--min", type=int, default=2, help="Min occurrences to report as duplicate.")
    behavior_group.add_argument("--parallel", action="store_true", help="Scan files in parallel.")
    behavior_group.add_argument("--use-multiprocessing", action="store_true", help="Use multiprocessing instead of threading.")
    behavior_group.add_argument("--max-workers", type=int, help="Max workers for parallel processing.")
    
    # Output & Misc
    output_group = parser.add_argument_group("Output & Misc")
    output_group.add_argument("-p", "--preview", action="store_true", help="Show formatted preview of duplicates.")
    output_group.add_argument("--json", action="store_true", help="Output as JSON.")
    output_group.add_argument("--fail", action="store_true", help="Exit 1 if duplicates found.")
    output_group.add_argument("--verbose", action="store_true", help="Print detailed logs.")
    output_group.add_argument("--audit", action="store_true", help="Enable audit logging for file access trails (JSONL).")
    output_group.add_argument("--audit-log", type=str, help="Path for audit log output (defaults to .duplifinder_audit.jsonl).")
    output_group.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    return parser


def build_config(args: argparse.Namespace) -> Config:
    """Merge CLI args with config file (if provided); validate via Pydantic."""
    # Load config file if specified
    config_dict = {}
    if args.config:
        config_dict = load_config_file(args.config)

    root_candidates = args.root or config_dict.get("root", ["."])
    root_str = root_candidates[0] if len(root_candidates) > 0 and pathlib.Path(root_candidates[0]).exists() and pathlib.Path(root_candidates[0]).is_dir() else "."
    extra = root_candidates[1:] if len(root_candidates) > 1 else []

    # Setup logging early
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # Merge into dict for Pydantic
    merged = {
        "root": root_str,
        "ignore_dirs": {x.strip() for x in (args.ignore or config_dict.get("ignore", "")).split(",") if x.strip()},
        "exclude_patterns": {x.strip() for x in (args.exclude_patterns or config_dict.get("exclude_patterns", "")).split(",") if x.strip()},
        "exclude_names": {x.strip() for x in (args.exclude_names or config_dict.get("exclude_names", "")).split(",") if x.strip()},
        "filter_regexes": args.find_regex or config_dict.get("find_regex", []),
        "pattern_regexes": args.pattern_regex or config_dict.get("pattern_regex", []),  # Fixed: singular
        "search_specs": args.search or config_dict.get("search", []),
        "search_mode": bool(args.search or config_dict.get("search", [])),
        "token_mode": args.token_mode or config_dict.get("token_mode", False),
        "similarity_threshold": args.similarity_threshold or config_dict.get("similarity_threshold", 0.8),
        "dup_threshold": args.dup_threshold or config_dict.get("dup_threshold", 0.1),
        "json_output": args.json or config_dict.get("json", False),
        "fail_on_duplicates": args.fail or config_dict.get("fail", False),
        "min_occurrences": args.min or config_dict.get("min", 2),
        "verbose": args.verbose or config_dict.get("verbose", False),
        "parallel": args.parallel or config_dict.get("parallel", False),
        "use_multiprocessing": args.use_multiprocessing or config_dict.get("use_multiprocessing", False),
        "max_workers": args.max_workers or config_dict.get("max_workers", None),
        "preview": args.preview or config_dict.get("preview", False),
        "audit_enabled": args.audit or config_dict.get("audit", False),
        "audit_log_path": args.audit_log or config_dict.get("audit_log", ".duplifinder_audit.jsonl"),
        "respect_gitignore": not getattr(args, 'no_gitignore', False) and config_dict.get("respect_gitignore", True),
    }

    # Process find arguments
    find_args = (args.find or config_dict.get("find", [])) + extra
    types_to_search = set()
    filter_names = set()
    for item in find_args:
        if item in {"class", "def", "async_def"}:
            types_to_search.add(item)
        else:
            filter_names.add(item)
    if not types_to_search:
        types_to_search = {"class", "def", "async_def"}
    merged["types_to_search"] = types_to_search
    merged["filter_names"] = filter_names

    # Validate via Pydantic
    try:
        config = Config(**merged)
    except ValueError as e:
        logging.error(f"Config validation failed: {e}")
        raise SystemExit(2)  # Config error code

    # Merge ignore_dirs with defaults
    config.ignore_dirs = DEFAULT_IGNORES.union(config.ignore_dirs)

    return config
```

---

## token_finder.py

<a id='token-finder-py'></a>

```python
# src/duplifinder/token_finder.py

"""Token-based duplicate finder using similarity ratios."""

import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from .config import Config
from .processors import process_file_tokens
from .utils import discover_py_files, run_parallel, log_file_count


def find_token_duplicates(config: Config) -> Tuple[Dict[str, List[Tuple[str, str, float]]], List[str], int, int, int]:
    """Find token-based duplicates across the project, optionally in parallel; return total_lines, dup_lines."""
    all_similarities: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
    skipped: List[str] = []
    scanned = 0
    total_lines = 0
    dup_lines = 0  # Heuristic: refine with actual spans in future

    py_files = discover_py_files(config)
    log_file_count(py_files, config)

    for result in run_parallel(py_files, process_file_tokens, config=config):
        similarities, skipped_file, file_lines = result
        if isinstance(skipped_file, str):
            skipped.append(skipped_file)
            logging.debug(f"Skipped file: {skipped_file}")
        else:
            scanned += 1
            total_lines += file_lines
            for key, pairs in similarities.items():
                all_similarities[key].extend(pairs)
                dup_lines += len(pairs) * 20  # Avg block heuristic

    if config.verbose:
        logging.info(f"Scanned {scanned} files, skipped {len(skipped)}, total lines: {total_lines}, estimated dup lines: {dup_lines}")

    return all_similarities, skipped, scanned, total_lines, dup_lines
```

---

## utils.py

<a id='utils-py'></a>

```python
# src/duplifinder/utils.py

"""Shared utilities for file discovery and parallel execution."""

import concurrent.futures
import contextlib
import fnmatch
import json
import logging
import os
import mimetypes
import threading
import time
from pathlib import Path
from typing import Callable, Generator, List, Any, Dict, Optional

from tqdm import tqdm

from .config import Config  # <-- Make sure this import is here


def audit_log_event(config: Config, event_type: str, **kwargs) -> None:
    """Emit structured audit event to JSONL if enabled; thread/process-safe append."""
    if not config.audit_enabled:
        return
    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": event_type,
        "root": str(config.root),
        "user": os.environ.get("USER", "unknown"),
        "worker_id": threading.current_thread().name if not config.use_multiprocessing else os.getpid(),
        **kwargs,
    }
    try:
        with open(config.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
            f.flush()  # Ensure visibility in parallel
    except Exception as e:
        logging.warning(f"Audit log write failed: {e}")


# FIXED: Added config: Config argument
def _parse_gitignore(gitignore_path: Path, config: Config) -> List[str]:
    """Simple stdlib parser for .gitignore: lines as fnmatch patterns (basic support for ! negation)."""
    patterns = []
    negate = False
    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):  # Skip comments/empty
                    continue
                if line == "!":  # Negation toggle (basic handling)
                    negate = True
                    continue
                pattern = line
                if negate:
                    pattern = "!" + pattern  # Prefix for negation logic in filter
                    negate = False
                patterns.append(pattern)
        if config.verbose:
            logging.info(f"Parsed {len(patterns)} .gitignore patterns from {gitignore_path}")
        audit_log_event(config, "gitignore_parsed", path=str(gitignore_path), patterns_count=len(patterns))
        return patterns
    except Exception as e:
        logging.warning(f"Failed to parse .gitignore '{gitignore_path}': {e}")
        return []


# FIXED: Added config: Config argument
def _matches_gitignore(path: Path, patterns: List[str], config: Config) -> bool:
    """Check if path matches any .gitignore pattern (with negation support)."""
    rel_path = path.relative_to(config.root).as_posix()
    for pattern in patterns:
        if pattern.startswith("!"):  # Negation: skip if matches
            if fnmatch.fnmatch(rel_path, pattern[1:]):
                return False  # Explicit include overrides
        elif fnmatch.fnmatch(rel_path, pattern):
            return True  # Exclude match
    return False


def discover_py_files(config: Config) -> List[Path]:
    """Discover Python files, excluding ignored dirs, .gitignore patterns, and non-Py content."""
    gitignore_patterns: List[str] = []
    gitignore_path = config.root / ".gitignore"
    if config.respect_gitignore and gitignore_path.exists():
        # FIXED: Pass config
        gitignore_patterns = _parse_gitignore(gitignore_path, config)

    candidates = [
        p for p in config.root.rglob("*.py")
        if not any(part in config.ignore_dirs for part in p.parts)
        # FIXED: Pass config
        and not _matches_gitignore(p, gitignore_patterns, config)
    ]
    py_files = []
    for p in candidates:
        # Audit: Log discovery attempt
        try:
            stat = p.stat()
            audit_log_event(config, "file_discovered", path=str(p), size=stat.st_size)
        except Exception:
            audit_log_event(config, "file_discovered", path=str(p), size=0, error="stat_failed")

        # Check MIME/content for non-Py masqueraders
        mime, _ = mimetypes.guess_type(str(p))
        if mime != "text/x-python":
            audit_log_event(config, "file_skipped", path=str(p), reason=f"MIME {mime}")
            logging.info(f"Skipping non-Py file '{p}': MIME {mime}")
            continue

        # Quick content check (first 1024 bytes)
        try:
            with open(p, "rb") as f:
                header = f.read(1024)
                if not (header.startswith(b"#!") or b"def " in header or b"class " in header):
                    audit_log_event(config, "file_skipped", path=str(p), reason="No Python markers")
                    logging.info(f"Skipping non-Py content '{p}': No Python markers")
                    continue
        except Exception:
            audit_log_event(config, "file_skipped", path=str(p), reason="header_read_failed")
            continue  # FIXED: Do not append this file

        py_files.append(p)
        audit_log_event(config, "file_accepted", path=str(p))

    return py_files


def run_parallel(
    py_files: List[Path],
    process_fn: Callable,
    *args,
    config: Config,
    **kwargs
) -> Generator[Any, None, None]:
    """Shared parallel execution logic (generator)."""
    if config.max_workers is None:
        config.max_workers = os.cpu_count() or 4
    executor_cls = concurrent.futures.ProcessPoolExecutor if config.use_multiprocessing else concurrent.futures.ThreadPoolExecutor
    with executor_cls(max_workers=config.max_workers) if config.parallel else contextlib.nullcontext() as executor:
        if config.parallel:
            futures = []
            for idx, p in enumerate(py_files):
                future = executor.submit(process_fn, p, *args, config=config, **kwargs)
                # Audit: Log task dispatch
                audit_log_event(config, "task_submitted", file_path=str(p), future_id=id(future), index=idx)
                futures.append(future)
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(py_files), disable=not config.verbose, desc="Processing files"):
                result = future.result()
                # Audit: Log completion (basic; detailed in processors)
                audit_log_event(config, "task_completed", future_id=id(future), success=True, error=None)
                yield result
        else:
            for py_file in tqdm(py_files, disable=not config.verbose, desc="Processing files"):
                # Audit: Log sequential dispatch
                audit_log_event(config, "task_submitted", file_path=str(py_file), future_id=None, index=None)
                result = process_fn(py_file, *args, config=config, **kwargs)
                audit_log_event(config, "task_completed", file_path=str(py_file), success=True, error=None)
                yield result


def log_file_count(py_files: List[Path], config: Config, context: str = "process") -> None:
    """Log the number of files discovered."""
    count = len(py_files)
    if config.verbose:
        logging.info(f"Found {count} Python files to {context}.")
    # Audit: Summary event
    audit_log_event(config, "discovery_summary", file_count=count, context=context)
```

---

## token_processor.py

<a id='token-processor-py'></a>

```python
# src/duplifinder/token_processor.py

"""Token file processor for similarity detection."""

import difflib
import fnmatch
import io
import logging
import tokenize
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import ast

from .config import Config
from .utils import audit_log_event


def tokenize_block(text: str) -> List[str]:
    """Tokenize a code block into normalized tokens."""
    tokens = []
    try:
        for token in tokenize.tokenize(io.BytesIO(text.encode('utf-8', errors='replace')).readline):
            if token.type not in (tokenize.COMMENT, tokenize.NL, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
                tokens.append(token.string.strip())
    except tokenize.TokenError:
        pass
    return tokens


def process_file_tokens(py_file: Path, config: Config) -> Tuple[Dict[str, List[Tuple[str, str, float]]], str | None, int]:
    """Process a single Python file for token-based duplicates; return total_lines."""
    str_py_file = str(py_file)
    if any(fnmatch.fnmatch(py_file.name, pat) for pat in config.exclude_patterns):
        if config.verbose:
            logging.info(f"Skipping {str_py_file}: matches exclude pattern")
        audit_log_event(config, "file_skipped", path=str_py_file, reason="exclude_pattern_match")
        return {}, str_py_file, 0

    total_lines = 0
    try:
        # Audit: Log open attempt
        audit_log_event(config, "file_opened", path=str_py_file, action="token_open")
        # Encoding-aware open
        with open(py_file, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        bytes_read = len(text)
        total_lines = len(text.splitlines())
        audit_log_event(config, "file_parsed", path=str_py_file, action="token_success", bytes_read=bytes_read, lines=total_lines)
        
        # Extract code blocks (simple: split on def/class, or use AST for bodies)
        tree = ast.parse(text, filename=str_py_file)
        blocks = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Extract body lines via lineno/end_lineno
                lines = text.splitlines()
                start = node.lineno - 1
                end = (node.end_lineno or node.lineno) 
                block_text = '\n'.join(lines[start:end])
                blocks.append((f"{node.lineno}:{end}", tokenize_block(block_text)))
        
        # Self-compare blocks for similarity (intra-file for now; extend later)
        similarities: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
        for i, (loc1, tokens1) in enumerate(blocks):
            for j, (loc2, tokens2) in enumerate(blocks[i+1:], i+1):
                matcher = difflib.SequenceMatcher(None, tokens1, tokens2)
                ratio = matcher.ratio()
                if ratio >= config.similarity_threshold:
                    key = f"token similarity >{int(config.similarity_threshold*100)}%"
                    similarities[key].append((f"{str_py_file}:{loc1}", f"{str_py_file}:{loc2}", ratio))
        
        return similarities, None, total_lines
    except UnicodeDecodeError as e:
        reason = f"encoding_error: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.warning(f"Skipping {str_py_file} due to encoding error: {e}")
        return {}, str_py_file, 0
    except Exception as e:
        reason = f"{type(e).__name__}: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.error(f"Skipping {str_py_file} for tokens: {reason}", exc_info=config.verbose)
        return {}, str_py_file, 0
```

---

