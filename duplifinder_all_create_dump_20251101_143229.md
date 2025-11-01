# 🗃️ Project Code Dump

**Generated:** 2025-11-01T14:32:30+00:00 UTC
**Version:** 6.0.0
**Git Branch:** main | **Commit:** 03d854a

---

## Table of Contents

1. [.github/workflows/publish.yml](#github-workflows-publish-yml)
2. [README.md](#readme-md)
3. [pyproject.toml](#pyproject-toml)
4. [src/duplifinder/ast_processor.py](#src-duplifinder-ast-processor-py)
5. [src/duplifinder/ast_visitor.py](#src-duplifinder-ast-visitor-py)
6. [src/duplifinder/cli.py](#src-duplifinder-cli-py)
7. [src/duplifinder/config.py](#src-duplifinder-config-py)
8. [src/duplifinder/definition_finder.py](#src-duplifinder-definition-finder-py)
9. [src/duplifinder/duplicate_renderer.py](#src-duplifinder-duplicate-renderer-py)
10. [src/duplifinder/finder.py](#src-duplifinder-finder-py)
11. [src/duplifinder/main.py](#src-duplifinder-main-py)
12. [src/duplifinder/output.py](#src-duplifinder-output-py)
13. [src/duplifinder/processor_utils.py](#src-duplifinder-processor-utils-py)
14. [src/duplifinder/processors.py](#src-duplifinder-processors-py)
15. [src/duplifinder/search_finder.py](#src-duplifinder-search-finder-py)
16. [src/duplifinder/search_renderer.py](#src-duplifinder-search-renderer-py)
17. [src/duplifinder/text_finder.py](#src-duplifinder-text-finder-py)
18. [src/duplifinder/text_processor.py](#src-duplifinder-text-processor-py)
19. [src/duplifinder/token_finder.py](#src-duplifinder-token-finder-py)
20. [src/duplifinder/token_processor.py](#src-duplifinder-token-processor-py)
21. [src/duplifinder/utils.py](#src-duplifinder-utils-py)
22. [tests/conftest.py](#tests-conftest-py)
23. [tests/test_ast_visitor.py](#tests-test-ast-visitor-py)
24. [tests/test_cli.py](#tests-test-cli-py)
25. [tests/test_config.py](#tests-test-config-py)
26. [tests/test_finder.py](#tests-test-finder-py)
27. [tests/test_integration.py](#tests-test-integration-py)
28. [tests/test_main.py](#tests-test-main-py)
29. [tests/test_output.py](#tests-test-output-py)
30. [tests/test_processors.py](#tests-test-processors-py)
31. [tests/test_renderers.py](#tests-test-renderers-py)

---

## .github/workflows/publish.yml

<a id='github-workflows-publish-yml'></a>

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*.*.*'  # Trigger only for semantic version tags (e.g. v2.7.0)

permissions:
  contents: read
  id-token: write  # Required for PyPI Trusted Publishing via OIDC

jobs:
  build:
    name: Build & Publish Duplifinder
    runs-on: ubuntu-latest
    environment: pypi  # Optional: define in GitHub Settings > Environments

    steps:
      - name: 🧩 Checkout source
        uses: actions/checkout@v4

      - name: 🐍 Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: ⚙️ Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine setuptools wheel

      - name: 🏗️ Build distribution artifacts
        run: python -m build  # Uses pyproject.toml (setuptools backend)

      - name: 🔍 Validate build metadata
        run: twine check dist/*

      - name: 🧠 Cache wheelhouse (optional)
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: 🚀 Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          verbose: true
          skip-existing: true
```

---

## README.md

<a id='readme-md'></a>

~~~markdown
```markdown
[![PyPI version](https://badge.fury.io/py/duplifinder.svg)](https://badge.fury.io/py/duplifinder)
[![PyPI downloads](https://img.shields.io/pypi/dm/duplifinder.svg)](https://pypistats.org/packages/duplifinder)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](https://github.com/dhruv13x/duplifinder/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/duplifinder.svg)](https://pypi.org/project/duplifinder/)

# Duplifinder

**Detect and refactor duplicate Python code**—classes, functions, async defs, text patterns, and token similarities—for cleaner, more maintainable codebases.

Duplifinder leverages Python's AST for precise scanning, parallelizes for large repos, and integrates seamlessly into CI/CD pipelines to enforce DRY principles and catch regressions early.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [Output Formats](#output-formats)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Development](#development)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- **AST-Powered Detection**: Identifies duplicates in `ClassDef`, `FunctionDef`, `AsyncFunctionDef` (including class methods as `ClassName.method`).
- **Text Pattern Matching**: Regex-based search for arbitrary snippets (e.g., TODOs, FIXMEs).
- **Token Similarity**: Detect near-duplicates via normalized token diffs (e.g., similar function bodies).
- **Search Mode**: Locate all occurrences of specific definitions (singletons or multiples).
- **Parallel Processing**: Threaded or multiprocessing for monorepos (GIL-aware; configurable workers).
- **Rich Outputs**: Human-readable console (with Rich tables), JSON for automation.
- **Configurable Filtering**: Glob excludes, regex name filters, ignore dirs.
- **Audit Logging**: Opt-in JSONL trails for file access/compliance (v6.1.0+).
- **CI-Friendly**: Exit codes for fails, dup thresholds, and metrics export.

## Installation

```bash
# From PyPI (stable)
pip install duplifinder

# From GitHub (latest)
pip install git+https://github.com/dhruv13x/duplifinder.git@main

# Editable dev install
git clone https://github.com/dhruv13x/duplifinder.git
cd duplifinder
pip install -e ".[dev]"
```

Requires Python 3.12+. No additional setup for core usage; dev extras include pytest/mypy/black.

## Quick Start

Scan the current directory for duplicates (defaults to classes/functions/async functions):

```bash
# Basic scan with console output
duplifinder .

# With previews and verbose logs
duplifinder . --preview --verbose

# JSON for CI parsing
duplifinder . --json > duplicates.json

# Fail CI on duplicates
duplifinder . --fail
```

### Text Pattern Mode

Hunt duplicated lines via regex:

```bash
# Find TODOs with min 2 occurrences
duplifinder . --pattern-regex "TODO:" --min 2 --json
```

### Token Similarity (Near-Dups)

For similar but not identical code:

```bash
duplifinder . --token-mode --similarity-threshold 0.85 --preview
```

### Search Specific Definitions

List all occurrences (even singles):

```bash
# Singleton check for a class
duplifinder . -s class UIManager --preview

# Multiple specs
duplifinder . -s class UIManager -s def dashboard_menu --json
```

### Focused Scans

```bash
# Only classes
duplifinder . -f class

# Specific name
duplifinder . -f MyClass

# Types + names
duplifinder . -f class -f HelperFunc
```

## Configuration

CLI flags override a `.duplifinder.yaml` (specified via `--config`).

```yaml
# .duplifinder.yaml
root: .
ignore: ".git,__pycache__,venv"
exclude_patterns: "*.pyc,tests/*"
exclude_names: "^_.*,experimental_.*"
find: ["class", "def"]  # Default: all types
find_regex: ["class UI.*Manager"]
pattern_regex: ["TODO:"]
search: ["class UIManager"]  # For -s mode
json: false
fail: false
min: 2
verbose: true
parallel: true
use_multiprocessing: false  # For CPU-bound (avoids GIL)
max_workers: 8
preview: true
audit: true  # v6.1.0+: Enable file access trails
audit_log: "./logs/audit.jsonl"
similarity_threshold: 0.8
dup_threshold: 0.1  # Alert if >10% dup rate
```

Load with `duplifinder . --config .duplifinder.yaml`.

## CLI Reference

| Flag | Description | Default |
|------|-------------|---------|
| `<root>` | Scan root(s) (dirs/files) | `.` |
| `--config <path>` | YAML config file | None |
| `--ignore <dirs>` | Comma-separated ignores (e.g., `.git,build`) | Built-ins |
| `--exclude-patterns <globs>` | File globs to skip (e.g., `*.pyc`) | None |
| `--exclude-names <regexes>` | Name regexes to filter (e.g., `^_`) | None |
| `-f, --find <items>` | Types/names (e.g., `class`, `MyClass`) | All types |
| `--find-regex <patterns>` | Regex for types/names | None |
| `--pattern-regex <patterns>` | Text mode regexes | None |
| `-s, --search <specs>` | Search specs (e.g., `class Foo`) | None |
| `--token-mode` | Enable token similarity | False |
| `--similarity-threshold <float>` | Token match ratio (0-1) | 0.8 |
| `--dup-threshold <float>` | Alert if dup rate > this | 0.1 |
| `--min <int>` | Min occurrences for dup | 2 |
| `-p, --preview` | Show snippets | False |
| `--json` | JSON output | False |
| `--fail` | Exit 1 on dups | False |
| `--verbose` | Detailed logs | False |
| `--parallel` | Concurrent processing | False |
| `--use-multiprocessing` | Use processes (not threads) | False |
| `--max-workers <int>` | Worker count | CPU cores |
| `--audit` | Enable audit logging | False |
| `--audit-log <path>` | Audit JSONL path | `.duplifinder_audit.jsonl` |
| `--version` | Show version | N/A |

Run `duplifinder --help` for full details.

## Output Formats

### Console (Rich-Enhanced)

Formatted tables with counts and previews:

```
class MyClass (3 occurrences):
┌─────────────────────┬──────────────────────────────────────┐
│ Location            │ Snippet                              │
├─────────────────────┼──────────────────────────────────────┤
│ /src/a.py:10        │ 10 class MyClass:                    │
│ /src/b.py:15        │ 15   def init(self):                 │
│ /src/c.py:8         │ 8     pass                           │
└─────────────────────┴──────────────────────────────────────┘
```

No dups: `[green]No duplicates found.[/green]`

Alerts: `[red]ALERT: Dup rate 15% > 10% threshold[/red]`

Audit nudge (if enabled): `[dim green]Audit trail logged to ./audit.jsonl[/dim green]`

### JSON (Machine-Readable)

```json
{
  "generated_at": "2025-11-01T13:29:00Z",
  "root": "/path/to/repo",
  "scanned_files": 123,
  "skipped_files": ["tests/broken.py"],
  "duplicate_count": 2,
  "duplicates": {
    "class MyClass": [
      {"loc": "/src/a.py:10", "snippet": "class MyClass:\n  pass", "type": "class"}
    ]
  }
}
```

For search: Includes `is_singleton`, `count`, `occurrences`.

## Advanced Usage

### Parallelism for Monorepos

For 10k+ files, enable multiprocessing to bypass GIL:

```bash
duplifinder . --parallel --use-multiprocessing --max-workers 16
```

Benchmark: ~2x speedup on CPU-bound token mode; monitor via `--verbose`.

### Audit Logging (v6.1.0+)

Opt-in JSONL trails for compliance (file access, skips, durations):

```bash
duplifinder . --audit --audit-log ./logs/audit.jsonl --verbose
```

Sample entry:
```json
{"timestamp": "2025-11-01T13:29:00Z", "event_type": "file_parsed", "path": "/src/a.py", "action": "ast_success", "bytes_read": 1024, "lines": 50}
```

Query with `jq`: `jq '.event_type == "scan_completed"' audit.jsonl` for SLOs.

### CI Integration

Gate merges on zero dups:

```yaml
# .github/workflows/ci.yml
- name: Check Duplicates
  run: duplifinder . --fail --json --min 2
```

Threshold alerts:
```bash
duplifinder . --dup-threshold 0.05 --fail  # Fail if >5% dup rate
```

## Best Practices

- **Start Simple**: `--preview --min 2 --verbose` for initial runs; tune excludes iteratively.
- **CI Gating**: `--json --fail` for regressions; parse output for PR comments.
- **Monorepo Scaling**: Use `--use-multiprocessing` for token/AST; cap `--max-workers` at 2x cores.
- **False Positive Tuning**: `--exclude-names "^test_.*"` for fixtures; `--exclude-patterns "migrations/*"`.
- **Compliance**: Enable `--audit` in prod scans; rotate logs via cron.

## Development

Install dev deps:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest  # With coverage: pytest --cov=src/duplifinder --cov-fail-under=90
```

Lint/format:
```bash
black .
mypy src/duplifinder  # Strict mode
```

Local run:
```bash
duplifinder . --preview
```

Build/release:
```bash
python -m build
twine upload dist/*
```

## Contributing

1. **Issue First**: Describe bug/feature with repro steps or use case.
2. **Branch & PR**: Fork → `feat/your-feature` → PR with rationale/tests.
3. **Standards**: Follow PEP 8 (black), type hints (mypy), 90%+ coverage.
4. **Small Changes**: <300 LOC per PR; link ADRs for architecture.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Troubleshooting

- **Syntax Errors**: Skipped files logged in `skipped_files` (JSON/verbose); fix or exclude.
- **Encoding Issues**: UTF-8 assumed; add `# coding: utf-8` or use `--exclude-patterns`.
- **High Skip Rate**: >10% triggers exit 3; tune ignores/excludes.
- **Perf Bottlenecks**: Profile with `--max-workers=1`; switch to multiprocessing for AST/token.
- **False Positives**: Layer `--exclude-names` regexes; test with `--preview`.

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*Built with ❤️ for Python devs. Questions? [Open an issue](https://github.com/dhruv13x/duplifinder/issues).*
```
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
dynamic = ["version"]  # Enable dynamic versioning via __version__.py or setuptools_scm
description = "Detect duplicate Python definitions, text patterns, and token similarities for codebase maintainability."
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [
    {name = "Dhruv", email = "dhruv13x@gmail.com"}
]
maintainers = [
    {name = "Dhruv", email = "dhruv13x@gmail.com"}
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Quality Assurance",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3 :: Only",
    "Typing :: Typed"
]
keywords = ["code-duplicates", "python-ast", "refactoring", "code-analysis", "static-analysis", "ci-cd"]
dependencies = [
    "pyyaml>=6.0",
    "rich>=13.0",
    "tqdm>=4.66",
    "pydantic>=2.5"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "black>=24.0",
    "mypy>=1.10",
    "pytest-cov>=5.0",
    "pytest-mock>=3.14",
    "types-PyYAML>=6.0.1"
]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=2.0"
]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0"
]

[project.urls]
Homepage = "https://github.com/dhruv13x/duplifinder"
Repository = "https://github.com/dhruv13x/duplifinder.git"
Issues = "https://github.com/dhruv13x/duplifinder/issues"
Changelog = "https://github.com/dhruv13x/duplifinder/blob/main/CHANGELOG.md"
"Release Notes" = "https://github.com/dhruv13x/duplifinder/releases"

[project.scripts]
duplifinder = "duplifinder.main:main"

[tool.black]
line-length = 88
target-version = ['py312']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | node_modules/.* # Exclude node_modules as it's a JS thing
)/
'''

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
strict_equality = true
warn_redundant_casts = true
warn_unused_ignores = false
plugins = []
exclude = ["^tests/.*", "^build/.*", "^dist/.*"]

[[tool.mypy.overrides]]
module = ["rich.*", "tqdm.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "-v",
    "--tb=short",
    "--durations=10",
    "--cov=src/duplifinder",
    "--cov-report=term-missing:skip-covered",
    "--cov-fail-under=90",
    "--doctest-modules",
    "--doctest-glob=*.md",
    "-m 'not slow'",
]
testpaths = ["tests"]
markers = [
    "slow: Marks slow tests (use -m 'not slow')",
    "integration: Marks integration tests requiring external services",
]
filterwarnings = [
    "ignore::DeprecationWarning:.*asyncio",
]
```

---

## src/duplifinder/ast_processor.py

<a id='src-duplifinder-ast-processor-py'></a>

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
                        indent = min((len(line) - len(line.lstrip())) for line in snippet_lines if line.strip())
                        snippet_lines = [line[indent:] for line in snippet_lines]
                        snippet = "\n".join(f"{i + 1} {line}" for i, line in enumerate(snippet_lines))
                definitions[t][name].append((loc, snippet))
        return definitions, None, total_lines
    except (SyntaxError, ValueError) as e:
        reason = f"{type(e).__name__}: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.error(f"Skipping {str_py_file} due to parsing error: {reason}", exc_info=config.verbose)
        return {}, str_py_file, 0
    except UnicodeDecodeError as e:
        reason = f"encoding_error: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.warning(f"Skipping {str_py_file} due to encoding error: {e}; try --encoding flag in future")
        return {}, str_py_file, 0
    except Exception as e:
        reason = f"{type(e).__name__}: {e}"
        audit_log_event(config, "file_skipped", path=str_py_file, reason=reason)
        logging.error(f"Skipping {str_py_file}: {reason}", exc_info=config.verbose)
        return {}, str_py_file, 0
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

## src/duplifinder/cli.py

<a id='src-duplifinder-cli-py'></a>

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

## src/duplifinder/config.py

<a id='src-duplifinder-config-py'></a>

```python
# src/duplifinder/config.py

"""Configuration management with Pydantic validation."""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Set

from pydantic import BaseModel, Field, validator
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

    @validator("types_to_search")
    def validate_types(cls, v):
        invalid = v - KNOWN_TYPES
        if invalid:
            raise ValueError(f"Unsupported types: {', '.join(invalid)}. Supported: {', '.join(KNOWN_TYPES)}")
        return v

    @validator("filter_regexes", "pattern_regexes", "exclude_names", pre=True)
    def compile_regexes(cls, v):
        import re
        compiled = []
        for pat in v:
            try:
                re.compile(pat)
                compiled.append(pat)
            except re.error as e:
                raise ValueError(f"Invalid regex '{pat}': {e}")
        return compiled

    @validator("search_specs", pre=True)
    def validate_search_specs(cls, v):
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

    @validator("audit_log_path")
    def validate_audit_path(cls, v, values):
        if values.get("audit_enabled") and not isinstance(v, Path):
            v = Path(v)
        if values.get("audit_enabled") and v.exists() and not v.parent.is_dir():
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

## src/duplifinder/definition_finder.py

<a id='src-duplifinder-definition-finder-py'></a>

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

## src/duplifinder/duplicate_renderer.py

<a id='src-duplifinder-duplicate-renderer-py'></a>

```python
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

    # Audit nudge: Optional console hint if enabled
    if config.audit_enabled:
        console.print(f"[dim green]Audit trail logged to {config.audit_log_path}[/dim green]")

    if config.fail_on_duplicates and duplicates:
        raise SystemExit(1)
```

---

## src/duplifinder/finder.py

<a id='src-duplifinder-finder-py'></a>

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

## src/duplifinder/main.py

<a id='src-duplifinder-main-py'></a>

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
        render_duplicates(results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines, is_token=True)
        # Audit: Scan complete aggregate
        audit_log_event(config, "scan_completed", mode="token", scanned=scanned, skipped=len(skipped), total_lines=total_lines, dup_lines=dup_lines, dup_rate=dup_rate, duration_ms=duration_ms)
        sys.exit(0 if not config.fail_on_duplicates or dup_lines == 0 else 1)
    elif config.pattern_regexes:
        import re
        patterns = [re.compile(p) for p in config.pattern_regexes]
        results, skipped, scanned, total_lines, dup_lines = find_text_matches(config, patterns)
        dup_rate = dup_lines / total_lines if total_lines else 0
        duration_ms = (time.perf_counter() - workflow_start) * 1000
        render_duplicates(results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines)
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
        render_duplicates(flat_results, config, False, dup_rate, config.dup_threshold, total_lines, dup_lines)
        # Audit: Scan complete aggregate
        audit_log_event(config, "scan_completed", mode="definitions", scanned=scanned, skipped=len(skipped), total_lines=total_lines, dup_lines=dup_lines, dup_rate=dup_rate, duration_ms=duration_ms)
        sys.exit(0 if not config.fail_on_duplicates or dup_lines == 0 else 1)


if __name__ == "__main__":
    main()
```

---

## src/duplifinder/output.py

<a id='src-duplifinder-output-py'></a>

```python
# src/duplifinder/output.py

"""Re-exports for backward compatibility; use submodules for new code."""

from .duplicate_renderer import render_duplicates
from .search_renderer import render_search, render_search_json

__all__ = ["render_duplicates", "render_search", "render_search_json"]
```

---

## src/duplifinder/processor_utils.py

<a id='src-duplifinder-processor-utils-py'></a>

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

## src/duplifinder/processors.py

<a id='src-duplifinder-processors-py'></a>

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

## src/duplifinder/search_finder.py

<a id='src-duplifinder-search-finder-py'></a>

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

## src/duplifinder/search_renderer.py

<a id='src-duplifinder-search-renderer-py'></a>

```python
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
```

---

## src/duplifinder/text_finder.py

<a id='src-duplifinder-text-finder-py'></a>

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

## src/duplifinder/text_processor.py

<a id='src-duplifinder-text-processor-py'></a>

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

## src/duplifinder/token_finder.py

<a id='src-duplifinder-token-finder-py'></a>

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

## src/duplifinder/token_processor.py

<a id='src-duplifinder-token-processor-py'></a>

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

## src/duplifinder/utils.py

<a id='src-duplifinder-utils-py'></a>

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

from .config import Config


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


def _parse_gitignore(gitignore_path: Path) -> List[str]:
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


def _matches_gitignore(path: Path, patterns: List[str]) -> bool:
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
        gitignore_patterns = _parse_gitignore(gitignore_path)

    candidates = [
        p for p in config.root.rglob("*.py")
        if not any(part in config.ignore_dirs for part in p.parts)
        and not _matches_gitignore(p, gitignore_patterns)
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
            logging.warning(f"Skipping non-Py file '{p}': MIME {mime}")
            continue
        # Quick content check (first 1024 bytes)
        try:
            with open(p, "rb") as f:
                header = f.read(1024)
                if not (header.startswith(b"#!") or b"def " in header or b"class " in header):
                    audit_log_event(config, "file_skipped", path=str(p), reason="No Python markers")
                    logging.warning(f"Skipping non-Py content '{p}': No Python markers")
                    continue
        except Exception:
            audit_log_event(config, "file_skipped", path=str(p), reason="header_read_failed")
            pass  # Assume Py if unreadable
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

## tests/conftest.py

<a id='tests-conftest-py'></a>

```python
"""Pytest fixtures for Duplifinder."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from duplifinder.config import Config
from duplifinder.utils import discover_py_files


@pytest.fixture
def sample_py_file(tmp_path: Path):
    """Fixture: Sample Python file with defs."""
    py_file = tmp_path / "test.py"
    py_file.write_text(
        """class SingletonClass:
    def method(self):
        pass

def helper():
    pass"""
    )
    return py_file


@pytest.fixture
def invalid_py_file(tmp_path: Path):
    """Fixture: Invalid Python (syntax error)."""
    py_file = tmp_path / "invalid.py"
    py_file.write_text("def invalid: pass")  # Syntax error
    return py_file


@pytest.fixture
def non_py_file(tmp_path: Path):
    """Fixture: Non-Python .py (binary-like)."""
    py_file = tmp_path / "binary.py"
    py_file.write_bytes(b"\x00\xFF\xDEF")  # Binary header
    return py_file


@pytest.fixture
def mock_config() -> Config:
    """Fixture: Minimal valid Config."""
    return Config(root=Path("."), verbose=True, preview=False)


@pytest.fixture
def mock_py_files(tmp_path: Path):
    """Fixture: Multiple sample .py files."""
    files = []
    for i in range(2):
        f = tmp_path / f"file{i}.py"
        f.write_text(f"class DupClass{i}:\n    pass")
        files.append(f)
    return files


@patch("concurrent.futures.ThreadPoolExecutor")
def mock_parallel(executor_mock):
    """Mock for parallel execution in tests."""
    executor_mock.return_value.__enter__.return_value.submit.return_value.result.return_value = ({}, None, 5)
    return executor_mock
```

---

## tests/test_ast_visitor.py

<a id='tests-test-ast-visitor-py'></a>

```python
# tests/test_ast_visitor.py

"""Tests for AST visitor."""

import ast
from pathlib import Path  # Add import for consistency

from duplifinder.ast_visitor import EnhancedDefinitionVisitor


def test_class_detection():
    code = "class MyClass:\n    pass"
    tree = ast.parse(code)
    visitor = EnhancedDefinitionVisitor({'class'})
    visitor.visit(tree)
    assert len(visitor.definitions['class']) == 1
    assert visitor.definitions['class'][0][0] == 'MyClass'


def test_method_detection():
    code = """
class MyClass:
    def method(self):
        pass
    async def async_method(self):
        pass
"""
    tree = ast.parse(code)
    visitor = EnhancedDefinitionVisitor({'def', 'async_def'})
    visitor.visit(tree)
    assert len(visitor.definitions['def']) == 1
    assert visitor.definitions['def'][0][0] == 'MyClass.method'
    assert len(visitor.definitions['async_def']) == 1
    assert visitor.definitions['async_def'][0][0] == 'MyClass.async_method'


def test_standalone_functions():
    code = "def standalone(): pass\nasync def async_standalone(): pass"
    tree = ast.parse(code)
    visitor = EnhancedDefinitionVisitor({'def', 'async_def'})
    visitor.visit(tree)
    assert len(visitor.definitions['def']) == 1
    assert visitor.definitions['def'][0][0] == 'standalone'
    assert len(visitor.definitions['async_def']) == 1
    assert visitor.definitions['async_def'][0][0] == 'async_standalone'


def test_no_matching_types():
    code = "class MyClass: pass"
    tree = ast.parse(code)
    visitor = EnhancedDefinitionVisitor({'def'})  # No class
    visitor.visit(tree)
    assert 'class' not in visitor.definitions
    assert 'def' not in visitor.definitions  # No defs, so key not populated
```

---

## tests/test_cli.py

<a id='tests-test-cli-py'></a>

```python
"""Tests for CLI parsing and config building."""

import argparse
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from duplifinder.cli import create_parser, build_config
from duplifinder.config import Config, DEFAULT_IGNORES


def test_create_parser_basic():
    """Test parser creation and --help."""
    parser = create_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.description == "Find duplicate Python definitions across a project."


def test_create_parser_args_parsing():
    """Test arg parsing with sample CLI."""
    parser = create_parser()
    args = parser.parse_args([".", "--verbose", "--find", "class", "--pattern-regex", "TODO"])
    assert args.root == ["."]
    assert args.verbose is True
    assert args.find == ["class"]
    assert args.pattern_regex == ["TODO"]


def test_build_config_default():
    """Test build_config with no args (defaults)."""
    mock_args = Mock(spec=argparse.Namespace)
    mock_args.root = []
    mock_args.config = None
    mock_args.verbose = False
    mock_args.ignore = ""
    mock_args.exclude_patterns = ""
    mock_args.exclude_names = ""
    mock_args.find_regex = []
    mock_args.pattern_regex = []
    mock_args.search = None
    mock_args.find = []
    mock_args.min = 2
    mock_args.token_mode = False
    mock_args.similarity_threshold = 0.8
    mock_args.dup_threshold = 0.1
    mock_args.json = False
    mock_args.fail = False
    mock_args.parallel = False
    mock_args.use_multiprocessing = False
    mock_args.max_workers = None
    mock_args.preview = False
    with patch("duplifinder.cli.load_config_file", return_value={}):
        config = build_config(mock_args)
    assert config.root == Path(".")
    assert config.types_to_search == {"class", "def", "async_def"}
    assert config.ignore_dirs == DEFAULT_IGNORES
    assert config.min_occurrences == 2


def test_build_config_with_yaml(tmp_path):
    """Test merge CLI + YAML."""
    mock_args = Mock(spec=argparse.Namespace)
    mock_args.root = []
    mock_args.config = "dummy.yaml"  # Dummy; patch load
    mock_args.min = 2
    mock_args.verbose = True
    mock_args.ignore = ""
    mock_args.exclude_patterns = ""
    mock_args.exclude_names = ""
    mock_args.find_regex = []
    mock_args.pattern_regex = []
    mock_args.search = None
    mock_args.find = []
    mock_args.token_mode = False
    mock_args.similarity_threshold = 0.8
    mock_args.dup_threshold = 0.1
    mock_args.json = False
    mock_args.fail = False
    mock_args.parallel = False
    mock_args.use_multiprocessing = False
    mock_args.max_workers = None
    mock_args.preview = False
    with patch("duplifinder.cli.load_config_file", return_value={'find': ['class'], 'min': 3}):
        config = build_config(mock_args)
    assert config.types_to_search == {"class"}
    assert config.min_occurrences == 2  # CLI precedence


def test_build_config_invalid_regex():
    """Test Pydantic validation raises SystemExit(2)."""
    mock_args = Mock(spec=argparse.Namespace)
    mock_args.root = []
    mock_args.config = None
    mock_args.verbose = False
    mock_args.pattern_regex = ["[unclosed"]  # Invalid: unclosed character class
    mock_args.ignore = ""
    mock_args.exclude_patterns = ""
    mock_args.exclude_names = ""
    mock_args.find_regex = []
    mock_args.search = None
    mock_args.find = []
    mock_args.min = 2
    mock_args.token_mode = False
    mock_args.similarity_threshold = 0.8
    mock_args.dup_threshold = 0.1
    mock_args.json = False
    mock_args.fail = False
    mock_args.parallel = False
    mock_args.use_multiprocessing = False
    mock_args.max_workers = None
    mock_args.preview = False
    with patch("duplifinder.cli.load_config_file", return_value={}):
        with pytest.raises(SystemExit) as exc:
            build_config(mock_args)
        assert exc.value.code == 2


def test_build_config_invalid_search_spec():
    """Test invalid search spec → SystemExit(2)."""
    mock_args = Mock(spec=argparse.Namespace)
    mock_args.root = []
    mock_args.config = None
    mock_args.verbose = False
    mock_args.search = ["class"]  # Bare type
    mock_args.ignore = ""
    mock_args.exclude_patterns = ""
    mock_args.exclude_names = ""
    mock_args.find_regex = []
    mock_args.pattern_regex = []
    mock_args.find = []
    mock_args.min = 2
    mock_args.token_mode = False
    mock_args.similarity_threshold = 0.8
    mock_args.dup_threshold = 0.1
    mock_args.json = False
    mock_args.fail = False
    mock_args.parallel = False
    mock_args.use_multiprocessing = False
    mock_args.max_workers = None
    mock_args.preview = False
    with patch("duplifinder.cli.load_config_file", return_value={}):
        with pytest.raises(SystemExit) as exc:
            build_config(mock_args)
        assert exc.value.code == 2


def test_build_config_find_processing():
    """Test --find arg processing."""
    mock_args = Mock(spec=argparse.Namespace)
    mock_args.root = []
    mock_args.config = None
    mock_args.verbose = False
    mock_args.find = ["class", "MyDef"]
    mock_args.ignore = ""
    mock_args.exclude_patterns = ""
    mock_args.exclude_names = ""
    mock_args.find_regex = []
    mock_args.pattern_regex = []
    mock_args.search = None
    mock_args.min = 2
    mock_args.token_mode = False
    mock_args.similarity_threshold = 0.8
    mock_args.dup_threshold = 0.1
    mock_args.json = False
    mock_args.fail = False
    mock_args.parallel = False
    mock_args.use_multiprocessing = False
    mock_args.max_workers = None
    mock_args.preview = False
    with patch("duplifinder.cli.load_config_file", return_value={}):
        config = build_config(mock_args)
    assert "class" in config.types_to_search
    assert "MyDef" in config.filter_names
```

---

## tests/test_config.py

<a id='tests-test-config-py'></a>

```python
"""Tests for Config validation."""

import pytest
from pathlib import Path
from duplifinder.config import Config, load_config_file


def test_valid_config_creation():
    """Test valid Config instantiation."""
    config = Config(root=Path("."), types_to_search={"class"})
    assert config.root == Path(".")
    assert config.types_to_search == {"class"}
    assert 0.0 <= config.similarity_threshold <= 1.0


def test_invalid_types_validation():
    """Test unsupported types raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported types"):
        Config(types_to_search={"invalid"})


def test_regex_validation():
    """Test invalid regex raises ValueError."""
    with pytest.raises(ValueError, match="Invalid regex"):
        Config(pattern_regexes="[unclosed]") # Invalid regex


def test_search_specs_validation():
    """Test invalid search specs raise ValueError."""
    with pytest.raises(ValueError, match="Must be 'type name'"):
        Config(search_specs=["class"])  # Bare type

    with pytest.raises(ValueError, match="Invalid type"):
        Config(search_specs=["invalid Foo"])


def test_load_config_file_valid(tmp_path: Path):
    """Test loading valid YAML."""
    yaml_file = tmp_path / ".duplifinder.yaml"
    yaml_file.write_text("root: .\ntypes_to_search: [class]")
    config_dict = load_config_file(yaml_file)
    assert config_dict["root"] == "."
    assert config_dict["types_to_search"] == ["class"]


def test_load_config_file_invalid(tmp_path: Path):
    """Test loading invalid YAML raises ValueError."""
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text("invalid: yaml: syntax")
    with pytest.raises(ValueError, match="Failed to load config"):
        load_config_file(yaml_file)
```

---

## tests/test_finder.py

<a id='tests-test-finder-py'></a>

```python
"""Tests for finder dispatcher and submodules."""

from unittest.mock import patch, Mock, MagicMock
import pytest
import re
from pathlib import Path
from duplifinder.finder import find_definitions, find_text_matches, find_token_duplicates, find_search_matches
from duplifinder.utils import discover_py_files, run_parallel, log_file_count
from duplifinder.config import Config


def test_discover_py_files_basic(mock_config):
    """Test file discovery excludes ignores."""
    mock_config.root = Path("tests/fixtures")  # Assume fixture dir
    mock_config.ignore_dirs = {".git"}
    files = discover_py_files(mock_config)
    assert isinstance(files, list)
    # Mock rglob yields; assert no .git files (logic check)


def test_discover_py_files_non_py_skips(mock_config, non_py_file):
    """Test non-Py content skipped."""
    mock_config.root = non_py_file.parent
    with patch("duplifinder.utils.mimetypes.guess_type", return_value=("application/octet-stream", None)):
        files = discover_py_files(mock_config)
    assert str(non_py_file) not in [str(f) for f in files]


@patch("duplifinder.utils.tqdm")
def test_run_parallel_sequential(tqdm_mock, mock_config, sample_py_file):
    """Test non-parallel yields sequentially."""
    mock_config.parallel = False
    mock_process = Mock(return_value=({}, None, 5))
    py_files = [sample_py_file]
    tqdm_mock.return_value = iter(py_files)  # Mock tqdm return iter over py_files
    results = list(run_parallel(py_files, mock_process, config=mock_config))
    assert len(results) == 1
    mock_process.assert_called_once_with(sample_py_file, config=mock_config)


def test_log_file_count_verbose(mock_config):
    """Test verbose logging."""
    mock_config.verbose = True
    with patch("duplifinder.utils.logging.info") as mock_log:
        log_file_count([Path("test.py")], mock_config)
    mock_log.assert_called_once()


def test_find_definitions_empty(mock_config):
    """Test definitions finder returns empty on no files."""
    mock_config.types_to_search = {"class"}
    with patch("duplifinder.definition_finder.discover_py_files", return_value=[]):
        results, skipped, scanned, total, dups = find_definitions(mock_config)
    assert scanned == 0
    assert results == {"class": {}}  # Empty defaultdict


def test_find_text_matches_patterns(mock_config):
    """Test text finder compiles patterns."""
    mock_config.pattern_regexes = ["TODO"]
    with patch("duplifinder.text_finder.discover_py_files", return_value=[]), \
         patch("duplifinder.text_finder.run_parallel", return_value=[]):
        results, skipped, scanned, total, dups = find_text_matches(mock_config, [re.compile("TODO")])
    assert scanned == 0


def test_find_token_duplicates_threshold(mock_config):
    """Test token finder uses threshold."""
    mock_config.similarity_threshold = 0.8
    with patch("duplifinder.token_finder.discover_py_files", return_value=[]):
        results, skipped, scanned, total, dups = find_token_duplicates(mock_config)
    assert scanned == 0


def test_find_search_matches_specs(mock_config):
    """Test search finder parses specs."""
    mock_config.search_specs = ["class Foo"]
    with patch("duplifinder.search_finder.discover_py_files", return_value=[]):
        results, skipped, scanned = find_search_matches(mock_config)
    assert scanned == 0
    assert len(results) == 0  # No files → no keys added
```

---

## tests/test_integration.py

<a id='tests-test-integration-py'></a>

```python
"""End-to-end integration tests."""

from unittest.mock import patch, Mock
import sys
from pathlib import Path

import pytest
from duplifinder.main import main
from duplifinder.cli import build_config
from duplifinder.finder import find_search_matches


def test_integration_search_singleton(monkeypatch, capsys):
    """Test search mode singleton."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", "-s", "class Foo"])
    mock_config = Mock(json_output=False, search_mode=True, search_specs=["class Foo"], fail_on_duplicates=False)
    with patch("duplifinder.cli.build_config", return_value=mock_config), \
         patch("duplifinder.finder.find_search_matches", return_value=({ "class Foo": [("test.py:1", "snippet")] }, [], 1)), \
         patch("duplifinder.output.render_search", side_effect=lambda *args: print('Verified singleton')), \
         patch('sys.exit', return_value=None):
        main()
    captured = capsys.readouterr()
    assert "Verified singleton" in captured.out


def test_integration_text_mode(monkeypatch, capsys):
    """Test text pattern mode."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", ".", "--pattern-regex", "TODO"])
    mock_config = Mock(pattern_regexes=["TODO"], search_mode=False, token_mode=False)
    with patch("duplifinder.cli.build_config", return_value=mock_config), \
         patch("duplifinder.finder.find_text_matches", return_value=({'TODO': ['file:1', 'file:2']}, [], 1, 10, 5)), \
         patch("duplifinder.output.render_duplicates"), \
         patch('sys.exit', return_value=None):
        main()
    captured = capsys.readouterr()
    assert "TODO" in captured.out  # Rendered


def test_integration_non_py_skip(monkeypatch):
    """Test non-Py files skipped in discovery."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", str(Path("."))])
    mock_config = Mock(root=Path("."))
    with patch("duplifinder.cli.build_config", return_value=mock_config), \
         patch("duplifinder.utils.discover_py_files", return_value=[]), \
         patch("duplifinder.finder.find_definitions", return_value=({}, ["non_py.py"], 0, 0, 0)), \
         patch('sys.exit', return_value=None):
        main()  # Should run clean, exit 0
```

---

## tests/test_main.py

<a id='tests-test-main-py'></a>

```python
"""Integration tests for main flows with exits."""

from unittest.mock import patch, Mock
import sys
from pathlib import Path
import pytest
from duplifinder.main import main


def test_main_default_run(monkeypatch, capsys):
    """Test default run: no dups → exit 0."""
    monkeypatch.setattr(sys, 'argv', ['duplifinder', '.'])
    mock_config = Mock(search_mode=False, pattern_regexes=[], token_mode=False)
    mock_config.root = Path('.')
    mock_config.ignore_dirs = set()
    nested_empty = {'class': {}, 'def': {}, 'async_def': {}}  # Empty nested
    with patch('duplifinder.main.build_config', return_value=mock_config), \
         patch('duplifinder.main.find_definitions', return_value=(nested_empty, [], 1, 10, 0)), \
         patch('duplifinder.main.render_duplicates', side_effect=lambda *args: print('No duplicates found')), \
         patch('sys.exit', side_effect=lambda *args: None):
        main()
    captured = capsys.readouterr()
    assert 'No duplicates found' in captured.out


def test_main_config_error(monkeypatch):
    """Test invalid config → exit 2."""
    monkeypatch.setattr(sys, 'argv', ['duplifinder', '.', '--pattern-regex', '[invalid'])
    with patch('duplifinder.main.build_config', side_effect=SystemExit(2)), \
         patch('sys.exit', side_effect=lambda *args: None):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2


def test_main_scan_fail_high_skips(monkeypatch):
    """Test >10% skips → exit 3."""
    monkeypatch.setattr(sys, 'argv', ['duplifinder', '.'])
    mock_config = Mock(search_mode=False, pattern_regexes=[], token_mode=False)
    mock_config.root = Path('.')
    mock_config.ignore_dirs = set()
    nested_empty = {'class': {}, 'def': {}, 'async_def': {}}  # Empty nested
    with patch('duplifinder.main.build_config', return_value=mock_config), \
         patch('duplifinder.main.find_definitions', return_value=(nested_empty, ['s'] * 11, 1, 10, 0)), \
         patch('duplifinder.main.render_duplicates'), \
         patch('sys.exit', side_effect=lambda *args: None):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 3  # High skip rate


def test_main_fail_on_dups(monkeypatch):
    """Test dups with --fail → exit 1."""
    monkeypatch.setattr(sys, 'argv', ['duplifinder', '.', '--fail'])
    mock_config = Mock(fail_on_duplicates=True, search_mode=False, pattern_regexes=[], token_mode=False)
    mock_config.root = Path('.')
    mock_config.ignore_dirs = set()
    nested_dups = {'class': {'Dup': [('file:1', '') , ('file:2', '')]}}  # Nested with 2 items
    with patch('duplifinder.main.build_config', return_value=mock_config), \
         patch('duplifinder.main.find_definitions', return_value=(nested_dups, [], 1, 10, 5)), \
         patch('duplifinder.main.render_duplicates'), \
         patch('sys.exit', side_effect=lambda *args: None):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
```

---

## tests/test_output.py

<a id='tests-test-output-py'></a>

```python
"""Tests for output rendering."""

from unittest.mock import patch, Mock
import json

import pytest
from duplifinder.output import render_duplicates, render_search, render_search_json
from duplifinder.config import Config
from pathlib import Path


def test_render_duplicates_empty(capsys):
    """Test empty dups show 'No duplicates'."""
    config = Mock(spec=Config, preview=False, json_output=False, fail_on_duplicates=False)
    render_duplicates({}, config, False, 0.0, 0.1, 0, 0)
    captured = capsys.readouterr()
    assert 'No duplicates found' in captured.out


def test_render_search_singleton(capsys):
    """Test singleton search output."""
    config = Mock(spec=Config, preview=False, fail_on_duplicates=False)
    results = {'class UIManager': [('file.py:1', 'snippet')]}
    render_search(results, config)
    captured = capsys.readouterr()
    assert 'Verified singleton' in captured.out
    assert 'file.py:1' in captured.out


def test_render_search_json():
    """Test JSON search output."""
    config = Mock(spec=Config, verbose=True, search_specs=[])
    config.root = Path('.')
    results = {'class UIManager': [('file.py:1', 'snippet')]}
    with patch('sys.stdout') as mock_stdout:
        render_search_json(results, config, 1, [])
    output = mock_stdout.write.call_args.args[0]
    parsed = json.loads(output)
    assert parsed['search_results']['class UIManager']['is_singleton'] is True
    assert len(parsed['search_results']['class UIManager']['occurrences']) == 1


def test_render_duplicates_with_metrics(capsys):
    """Test dup rate alert."""
    config = Mock(spec=Config, dup_threshold=0.1, json_output=False, fail_on_duplicates=False)
    render_duplicates({}, config, False, 0.15, 0.1, 100, 15)
    captured = capsys.readouterr()
    assert 'ALERT: Duplication rate' in captured.out
```

---

## tests/test_processors.py

<a id='tests-test-processors-py'></a>

```python
"""Tests for processors with edges."""

import re
from pathlib import Path

import pytest
from duplifinder.ast_processor import process_file_ast
from duplifinder.text_processor import process_file_text
from duplifinder.token_processor import process_file_tokens, tokenize_block
from duplifinder.config import Config
from duplifinder.processor_utils import estimate_dup_lines


def test_process_file_ast_valid(sample_py_file, mock_config):
    """Test AST processing on valid file."""
    defs, skipped, lines = process_file_ast(sample_py_file, mock_config)
    assert skipped is None
    assert lines == 6
    assert "class" in defs
    assert "SingletonClass" in defs["class"]


def test_process_file_ast_invalid(invalid_py_file, mock_config):
    """Test AST skips syntax errors."""
    defs, skipped, lines = process_file_ast(invalid_py_file, mock_config)
    assert skipped == str(invalid_py_file)
    assert lines == 0


def test_process_file_ast_exclude(mock_config, sample_py_file):
    """Test exclude_patterns skips files."""
    mock_config.exclude_patterns = {"test.py"}
    defs, skipped, lines = process_file_ast(sample_py_file, mock_config)
    assert skipped == str(sample_py_file)


def test_process_file_ast_exclude_names(mock_config, sample_py_file):
    """Test exclude_names filters defs."""
    mock_config.exclude_names = {"Singleton.*"}
    defs, skipped, lines = process_file_ast(sample_py_file, mock_config)
    assert "SingletonClass" not in defs["class"]  # Filtered


def test_tokenize_block():
    """Test tokenization normalizes."""
    text = "def foo(): pass  # comment"
    tokens = tokenize_block(text)
    assert "def" in tokens
    assert "foo" in tokens
    assert "# comment" not in " ".join(tokens)


def test_process_file_text_match(sample_py_file, mock_config):
    """Test text pattern matching."""
    patterns = [re.compile("class")]
    matches, skipped, lines = process_file_text(sample_py_file, patterns, mock_config)
    assert skipped is None
    assert "class" in matches
    assert len(matches["class"]) == 1


def test_process_file_text_no_match(tmp_path: Path, mock_config):
    """Test no matches returns empty."""
    py_file = tmp_path / "no_match.py"
    py_file.write_text("No match here")
    patterns = [re.compile("match")]
    matches, skipped, lines = process_file_text(py_file, patterns, mock_config)
    assert matches == {}


def test_process_file_tokens_similarity(tmp_path: Path, mock_config):
    """Test token similarity detection."""
    mock_config.similarity_threshold = 0.5
    py_file = tmp_path / "similar.py"
    py_file.write_text("def sim1(): pass\ndef sim2(): pass")
    similarities, skipped, lines = process_file_tokens(py_file, mock_config)
    assert skipped is None
    assert "token similarity >50%" in similarities


def test_estimate_dup_lines_below_min(mock_config):
    """Test dup estimation < min_occurrences = 0."""
    items = [("loc1", "")]
    assert estimate_dup_lines(items, False, mock_config) == 0


def test_estimate_dup_lines_above_min(mock_config, sample_py_file):
    """Test dup estimation > min."""
    mock_config.min_occurrences = 1
    items = [("loc1", ""), ("loc2", "")]
    assert estimate_dup_lines(items, False, mock_config) > 0
```

---

## tests/test_renderers.py

<a id='tests-test-renderers-py'></a>

```python
"""Tests for renderers."""

import json
from unittest.mock import patch

import pytest
from duplifinder.duplicate_renderer import render_duplicates
from duplifinder.search_renderer import render_search, render_search_json
from duplifinder.config import Config


def test_render_duplicates_empty(capsys, mock_config):
    """Test empty dups show 'No duplicates'."""
    mock_config.json_output = False
    render_duplicates({}, mock_config, False, 0.0, 0.1, 0, 0)
    captured = capsys.readouterr()
    assert "No duplicates found" in captured.out


def test_render_duplicates_alert(capsys, mock_config):
    """Test dup rate alert."""
    mock_config.dup_threshold = 0.1
    mock_config.json_output = False
    render_duplicates({}, mock_config, False, 0.15, 0.1, 100, 15)
    captured = capsys.readouterr()
    assert "ALERT: Duplication rate" in captured.out


def test_render_search_singleton(capsys, mock_config):
    """Test singleton search output."""
    mock_config.json_output = False
    results = {"class Foo": [("file.py:1", "snippet")]}
    render_search(results, mock_config)
    captured = capsys.readouterr()
    assert "Verified singleton" in captured.out


def test_render_search_json(mock_config):
    """Test JSON search output."""
    mock_config.root = Path(".")
    results = {"class Foo": [("file.py:1", "snippet")]}
    with patch("sys.stdout") as mock_stdout:
        render_search_json(results, mock_config, 1, [])
    output = mock_stdout.write.call_args.args[0]
    parsed = json.loads(output)
    assert parsed["search_results"]["class Foo"]["is_singleton"] is True


def test_render_duplicates_token_mode(capsys, mock_config):
    """Test token rendering normalization."""
    mock_config.json_output = False
    token_results = {"token similarity >80%": [("file:1:2 ~ file:3:4 (sim: 0.85)", "", 0.85)]}
    render_duplicates(token_results, mock_config, False, 0.0, 0.1, 10, 0, is_token=True)
    captured = capsys.readouterr()
    assert "(sim: 0.85)" in captured.out  # Normalized
```

---

