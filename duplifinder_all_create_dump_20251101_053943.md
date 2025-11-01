# 🗃️ Project Code Dump

**Generated:** 2025-11-01T05:39:50+00:00 UTC
**Version:** 6.0.0

---

## Table of Contents

1. [README.md](#readme-md)
2. [pyproject.toml](#pyproject-toml)
3. [src/duplifinder.egg-info/SOURCES.txt](#src-duplifinder-egg-info-sources-txt)
4. [src/duplifinder.egg-info/dependency_links.txt](#src-duplifinder-egg-info-dependency-links-txt)
5. [src/duplifinder.egg-info/entry_points.txt](#src-duplifinder-egg-info-entry-points-txt)
6. [src/duplifinder.egg-info/requires.txt](#src-duplifinder-egg-info-requires-txt)
7. [src/duplifinder.egg-info/top_level.txt](#src-duplifinder-egg-info-top-level-txt)
8. [src/duplifinder/ast_visitor.py](#src-duplifinder-ast-visitor-py)
9. [src/duplifinder/cli.py](#src-duplifinder-cli-py)
10. [src/duplifinder/config.py](#src-duplifinder-config-py)
11. [src/duplifinder/finder.py](#src-duplifinder-finder-py)
12. [src/duplifinder/main.py](#src-duplifinder-main-py)
13. [src/duplifinder/output.py](#src-duplifinder-output-py)
14. [src/duplifinder/processors.py](#src-duplifinder-processors-py)

---

## README.md

<a id='readme-md'></a>

~~~markdown
# Duplifinder

Detect duplicate Python definitions.

## Install
```bash
pip install .
~~~

---

## pyproject.toml

<a id='pyproject-toml'></a>

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "duplifinder"
version = "2.7.0"
description = "Find duplicate Python definitions across projects"
readme = "README.md"
requires-python = ">=3.8"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "you@example.com" }
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent"
]
keywords = ["duplicates", "code-analysis", "python", "refactoring"]

dependencies = [
    "pyyaml>=6.0",
    "rich>=12.0; sys_platform != 'win32'",
    "tqdm>=4.0; sys_platform != 'win32'"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=23.0",
    "mypy>=1.0"
]

[project.urls]
Homepage = "https://github.com/yourusername/duplifinder"
Repository = "https://github.com/yourusername/duplifinder"
Issues = "https://github.com/yourusername/duplifinder/issues"

[project.scripts]
duplifinder = "duplifinder.main:main"
```

---

## src/duplifinder.egg-info/SOURCES.txt

<a id='src-duplifinder-egg-info-sources-txt'></a>

```text
README.md
pyproject.toml
src/duplifinder/__init__.py
src/duplifinder/ast_visitor.py
src/duplifinder/cli.py
src/duplifinder/config.py
src/duplifinder/finder.py
src/duplifinder/main.py
src/duplifinder/output.py
src/duplifinder/processors.py
src/duplifinder.egg-info/PKG-INFO
src/duplifinder.egg-info/SOURCES.txt
src/duplifinder.egg-info/dependency_links.txt
src/duplifinder.egg-info/entry_points.txt
src/duplifinder.egg-info/requires.txt
src/duplifinder.egg-info/top_level.txt
```

---

## src/duplifinder.egg-info/dependency_links.txt

<a id='src-duplifinder-egg-info-dependency-links-txt'></a>

```text


```

---

## src/duplifinder.egg-info/entry_points.txt

<a id='src-duplifinder-egg-info-entry-points-txt'></a>

```text
[console_scripts]
duplifinder = duplifinder.main:main

```

---

## src/duplifinder.egg-info/requires.txt

<a id='src-duplifinder-egg-info-requires-txt'></a>

```text
pyyaml>=6.0

[:sys_platform != "win32"]
rich>=12.0
tqdm>=4.0

[dev]
pytest>=7.0
black>=23.0
mypy>=1.0

```

---

## src/duplifinder.egg-info/top_level.txt

<a id='src-duplifinder-egg-info-top-level-txt'></a>

```text
duplifinder

```

---

## src/duplifinder/ast_visitor.py

<a id='src-duplifinder-ast-visitor-py'></a>

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

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if "class" in self.types_to_search:
            end_lineno = node.end_lineno if node.end_lineno is not None else node.lineno
            self.definitions["class"].append((node.name, node.lineno, end_lineno, ""))
        # Collect method names within classes
        if "def" in self.types_to_search or "async_def" in self.types_to_search:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    t = "def" if isinstance(item, ast.FunctionDef) else "async_def"
                    if t in self.types_to_search:
                        end_lineno = item.end_lineno if item.end_lineno is not None else item.lineno
                        self.definitions[t].append((f"{node.name}.{item.name}", item.lineno, end_lineno, ""))
        self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        for t in self.types_to_search:
            if isinstance(node, KNOWN_TYPES[t]) and not isinstance(node, ast.ClassDef):
                end_lineno = node.end_lineno if node.end_lineno is not None else node.lineno
                self.definitions[t].append((node.name, node.lineno, end_lineno, ""))
        super().generic_visit(node)

```

---

## src/duplifinder/cli.py

<a id='src-duplifinder-cli-py'></a>

```python
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
```

---

## src/duplifinder/config.py

<a id='src-duplifinder-config-py'></a>

```python
# duplifinder/src/duplifinder/duplifinder/config.py

"""Configuration handling for Duplifinder."""

import logging
import pathlib
import ast
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import yaml

DEFAULT_IGNORES = {
    ".git", "__pycache__", ".venv", "venv", "build", "dist", "node_modules",
}

KNOWN_TYPES = {
"class": ast.ClassDef,
"def": ast.FunctionDef,
"async_def": ast.AsyncFunctionDef,
}


@dataclass
class Config:
    """Configuration settings loaded from CLI or config file."""

    root: pathlib.Path
    ignore_dirs: Set[str]
    exclude_patterns: Set[str]
    exclude_names: Set[str]
    types_to_search: Set[str]
    filter_names: Set[str]
    filter_regexes: List[str]
    pattern_regexes: List[str]
    json_output: bool
    fail_on_duplicates: bool
    min_occurrences: int
    verbose: bool
    parallel: bool
    use_multiprocessing: bool
    max_workers: Optional[int]
    preview: bool


def load_config_file(config_path: str) -> Dict:
    """Load configuration from a YAML file."""
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logging.error(f"Failed to load config file {config_path}: {e}")
        return {}
```

---

## src/duplifinder/finder.py

<a id='src-duplifinder-finder-py'></a>

```python
# src/duplifinder/finder.py

"""Core finder logic for definitions and text matches."""

import concurrent.futures
import contextlib
import logging
import os
import re
from collections import defaultdict
from typing import Dict, List, Tuple
from pathlib import Path

from tqdm import tqdm

from .config import Config
from .processors import process_file_ast, process_file_text


def discover_py_files(config: Config) -> List[Path]:
    """Discover Python files, excluding ignored dirs."""
    return [
        p for p in config.root.rglob("*.py")
        if not any(part in config.ignore_dirs for part in p.parts)
    ]


def run_parallel(executor_cls, max_workers: int, py_files: List[Path], process_fn, *args, config: Config, **kwargs) -> Tuple[Dict, List[str], int]:
    """Shared parallel execution logic."""
    with executor_cls(max_workers=max_workers) if config.parallel else contextlib.nullcontext() as executor:
        if config.parallel:
            futures = [executor.submit(process_fn, p, *args, config=config, **kwargs) for p in py_files]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(py_files), disable=not config.verbose, desc="Processing files"):
                result, skipped_file = future.result()
                yield result, skipped_file  # Generator for aggregation
        else:
            for py_file in tqdm(py_files, disable=not config.verbose, desc="Processing files"):
                result, skipped_file = process_fn(py_file, *args, config=config, **kwargs)
                yield result, skipped_file


def find_definitions(config: Config) -> Tuple[Dict[str, Dict[str, List[Tuple[str, str]]]], List[str], int]:
    """Find definitions across the project using AST, optionally in parallel."""
    all_definitions: Dict[str, Dict[str, List[Tuple[str, str]]]] = {t: defaultdict(list) for t in config.types_to_search}
    skipped: List[str] = []
    scanned = 0

    py_files = discover_py_files(config)
    if config.verbose:
        logging.info(f"Found {len(py_files)} Python files to process.")

    if config.max_workers is None:
        config.max_workers = os.cpu_count() or 4

    executor_cls = concurrent.futures.ProcessPoolExecutor if config.use_multiprocessing else concurrent.futures.ThreadPoolExecutor

    for defs, skipped_file in run_parallel(executor_cls, config.max_workers, py_files, process_file_ast, config=config):
        if skipped_file:
            skipped.append(skipped_file)
        else:
            scanned += 1
        for t, name_locs in defs.items():
            for name, items in name_locs.items():
                all_definitions[t][name].extend(items)

    return all_definitions, skipped, scanned


def find_text_matches(config: Config, patterns: List[re.Pattern]) -> Tuple[Dict[str, List[str]], List[str], int]:
    """Find text matches across the project, optionally in parallel."""
    all_matches: Dict[str, List[str]] = defaultdict(list)
    skipped: List[str] = []
    scanned = 0

    py_files = discover_py_files(config)
    if config.verbose:
        logging.info(f"Found {len(py_files)} Python files to process.")

    if config.max_workers is None:
        config.max_workers = os.cpu_count() or 4

    executor_cls = concurrent.futures.ProcessPoolExecutor if config.use_multiprocessing else concurrent.futures.ThreadPoolExecutor

    for matches, skipped_file in run_parallel(executor_cls, config.max_workers, py_files, process_file_text, patterns, config=config):
        if skipped_file:
            skipped.append(skipped_file)
        else:
            scanned += 1
        for matched, locs in matches.items():
            all_matches[matched].extend(locs)

    return all_matches, skipped, scanned
```

---

## src/duplifinder/main.py

<a id='src-duplifinder-main-py'></a>

```python
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
```

---

## src/duplifinder/output.py

<a id='src-duplifinder-output-py'></a>

```python
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
```

---

## src/duplifinder/processors.py

<a id='src-duplifinder-processors-py'></a>

```python
# src/duplifinder/processors.py

"""File processors for AST and text-based scanning."""

import fnmatch
import logging
import re
import tokenize
from collections import defaultdict
from typing import Dict, List, Tuple

import ast
from pathlib import Path

from .ast_visitor import EnhancedDefinitionVisitor
from .config import Config


def process_file_ast(py_file: Path, config: Config) -> Tuple[Dict[str, Dict[str, List[Tuple[str, str]]]], str | None]:
    """Process a single Python file for definitions using AST."""
    str_py_file = str(py_file)
    if any(fnmatch.fnmatch(py_file.name, pat) for pat in config.exclude_patterns):
        if config.verbose:
            logging.info(f"Skipping {str_py_file}: matches exclude pattern")
        return {}, str_py_file

    try:
        with tokenize.open(py_file) as fh:
            text = fh.read()
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
                        indent = min((len(line) - len(line.lstrip())) for line in snippet_lines if line.strip())
                        snippet_lines = [line[indent:] for line in snippet_lines]
                        snippet = "\n".join(f"{i + 1} {line}" for i, line in enumerate(snippet_lines))
                definitions[t][name].append((loc, snippet))
        return definitions, None
    except (SyntaxError, ValueError) as e:
        logging.error(f"Skipping {str_py_file} due to parsing error: {type(e).__name__}: {e}", exc_info=config.verbose)
        return {}, str_py_file
    except Exception as e:
        logging.error(f"Skipping {str_py_file}: {type(e).__name__}: {e}", exc_info=config.verbose)
        return {}, str_py_file


def process_file_text(py_file: Path, patterns: List[re.Pattern], config: Config) -> Tuple[Dict[str, List[str]], str | None]:
    """Process a single Python file for text patterns."""
    str_py_file = str(py_file)
    if any(fnmatch.fnmatch(py_file.name, pat) for pat in config.exclude_patterns):
        if config.verbose:
            logging.info(f"Skipping {str_py_file}: matches exclude pattern")
        return {}, str_py_file

    try:
        with open(py_file, "r") as f:
            lines = f.readlines()
        matches: Dict[str, List[str]] = defaultdict(list)
        for lineno, line in enumerate(lines, 1):
            for pat in patterns:
                if pat.search(line):
                    matches[pat.pattern].append(f"{str_py_file}:{lineno}")
        return matches, None
    except Exception as e:
        logging.error(f"Skipping {str_py_file}: {type(e).__name__}: {e}", exc_info=config.verbose)
        return {}, str_py_file
```

---

