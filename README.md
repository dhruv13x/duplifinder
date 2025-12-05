<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/duplifinder/main/duplifinder_logo.png" alt="duplifinder logo" width="200"/>
</div>

<div align="center">

<!-- Package Info -->
[![PyPI version](https://img.shields.io/pypi/v/duplifinder.svg)](https://pypi.org/project/duplifinder/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Smart Update](https://img.shields.io/badge/smart-update-green.svg)](https://github.com/dhruv13x/duplifinder)
![Wheel](https://img.shields.io/pypi/wheel/duplifinder.svg)
[![Release](https://img.shields.io/badge/release-PyPI-blue)](https://pypi.org/project/duplifinder/)

<!-- Build & Quality -->
[![Build status](https://github.com/dhruv13x/duplifinder/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/duplifinder/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/duplifinder/graph/badge.svg)](https://codecov.io/gh/dhruv13x/duplifinder)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](https://github.com/dhruv13x/duplifinder/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Security](https://img.shields.io/badge/security-CodeQL-blue.svg)

<!-- Usage -->
![Downloads](https://img.shields.io/pypi/dm/duplifinder.svg)
![OS](https://img.shields.io/badge/os-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)
[![Python Versions](https://img.shields.io/pypi/pyversions/duplifinder.svg)](https://pypi.org/project/duplifinder/)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Docs -->
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://your-docs-link)

</div>

# Duplifinder

**Detect and refactor duplicate Python code**—classes, functions, async defs, text patterns, and token similarities—for cleaner, more maintainable codebases.

Duplifinder leverages Python's AST for precise scanning, parallelizes for large repos, and integrates seamlessly into CI/CD pipelines to enforce DRY principles and catch regressions early.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- `pip`

### Installation

```bash
# From PyPI (stable)
pip install duplifinder
```

### Usage Example

Scan your current directory immediately:

```bash
# Basic scan
duplifinder .

# Scan with preview and verbose logging
duplifinder . --preview --verbose
```

---

## ✨ Key Features

- **AST-Powered Detection**: Identifies duplicates in `ClassDef`, `FunctionDef`, `AsyncFunctionDef`.
- **Token Similarity**: Detect near-duplicates via normalized token diffs (e.g., similar function bodies).
- **Parallel Processing**: Threaded or multiprocessing support for monorepos (GIL-aware).
- **Search Mode**: Locate all occurrences of specific definitions (singletons or multiples).
- **Text Pattern Matching**: Regex-based search for arbitrary snippets (e.g., TODOs, FIXMEs).
- **Rich Outputs**: Human-readable console tables and machine-readable JSON.
- **Audit Logging**: Opt-in JSONL trails for file access and compliance.
- **CI-Friendly**: Exit codes for fails, dup thresholds, and metrics export.

---

## ⚙️ Configuration & Advanced Usage

Duplifinder is highly configurable via CLI arguments or a `.duplifinder.yaml` file.

### CLI Reference

| Flag | Description | Default |
|------|-------------|---------|
| `<root>` | Scan root directory | `.` |
| `--config` | Path to YAML config file | None |
| `--ignore` | Comma-separated directories to ignore | Built-ins |
| `--exclude-patterns` | Comma-separated glob patterns | None |
| `--exclude-names` | Comma-separated regex patterns for names | None |
| `--no-gitignore` | Disable auto-respect of .gitignore | False |
| `-f, --find` | Types/names to find (class, def, async_def) | All |
| `--find-regex` | Regex patterns for types/names | None |
| `--pattern-regex` | Regex patterns for duplicate code snippets | None |
| `-s, --search` | Search specific definitions (e.g. `class User`) | None |
| `--token-mode` | Enable token-based duplication detection | False |
| `--similarity-threshold` | Similarity ratio (0.0-1.0) | 0.8 |
| `--dup-threshold` | Alert if dup rate > threshold | 0.1 |
| `--min` | Min occurrences to report | 2 |
| `--parallel` | Enable parallel scanning | False |
| `--use-multiprocessing` | Use multiprocessing (CPU-bound) | False |
| `--max-workers` | Max worker threads/processes | Auto |
| `-p, --preview` | Show code snippets in output | False |
| `--json` | Output results as JSON | False |
| `--fail` | Exit 1 if duplicates found | False |
| `--verbose` | Enable verbose logging | False |
| `--audit` | Enable audit logging | False |
| `--audit-log` | Path to audit log file | `.duplifinder_audit.jsonl` |
| `--version` | Show version information | - |

### Example `.duplifinder.yaml`

```yaml
root: .
ignore: "tests,docs"
exclude_patterns: "*.pyc, migrations/*"
token_mode: true
similarity_threshold: 0.85
fail: true
```

---

## 🏗️ Architecture

Duplifinder is built with modularity and performance in mind.

### Directory Structure

```
src/duplifinder/
├── main.py           # Entry point & orchestration
├── cli.py            # Argument parsing
├── config.py         # Configuration validation (Pydantic)
├── finder.py         # Dispatcher for different modes
├── definition_finder.py # AST-based duplicate finder
├── token_finder.py   # Token-based similarity finder
├── text_finder.py    # Regex pattern finder
├── processors.py     # File processing logic
├── output.py         # Output rendering (Rich/JSON)
└── utils.py          # Utilities & Logging
```

### Core Logic Flow
1.  **Entry**: `main.py` parses args via `cli.py` and builds `config.py`.
2.  **Dispatch**: Selects the appropriate finder (`definition`, `token`, or `text`) based on mode.
3.  **Process**: Files are scanned in parallel using `processors.py` to extract ASTs, tokens, or text.
4.  **Analyze**: Duplicates are identified based on hashes or similarity metrics.
5.  **Report**: Results are rendered to Console or JSON via `output.py`.

---

## 🗺️ Roadmap

We have an ambitious vision for Duplifinder. See [ROADMAP.md](ROADMAP.md) for details.

- **Foundation (Completed)**: AST detection, Token similarity, Parallel processing, Rich output.
- **The Standard (Upcoming)**: IDE Integration, Automated Refactoring Suggestions.
- **The Ecosystem (Future)**: GitHub Actions, Webhooks, Plugin Architecture.
- **Vision (God Level)**: AI-Powered Refactoring, Cross-Repository Analysis.

---

## 🤝 Contributing & License

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

**License**: MIT. See [LICENSE](LICENSE) for more information.

---

*Built with ❤️ for Python devs.*
