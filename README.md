```markdown
# Duplifinder

Detect duplicate Python definitions across a project (classes, functions, async functions, and text patterns).

Duplifinder scans a codebase and reports repeated definitions or matching text patterns so you can refactor, deduplicate, and improve maintainability.

## Highlights

- Fast, file-system friendly scanning using Python AST
- Detects duplicate class, def, and async def definitions (including methods inside classes)
- Text-pattern mode for arbitrary duplicate snippet detection via regex
- JSON output for integration into CI/CD pipelines
- Preview mode to show formatted definition snippets
- Parallel scanning with optional multiprocessing for large repositories
- Configurable via CLI flags or a YAML config file

## Quick install

```bash
# From project root (editable install)
pip install -e .

# Or build and install
pip install .
```

## Quick start

Scan the current repository for duplicate definitions (default: classes, functions, async functions):

```bash
# Run default scan and show results on console
duplifinder .

# Show preview snippets and verbose logging
duplifinder . --preview --verbose

# Fail CI if any duplicates found
duplifinder . --fail

# Output machine-readable JSON
duplifinder . --json > duplicates.json

# Token-based near-duplicates (e.g., similar function bodies)
duplifinder . --token-mode --similarity-threshold 0.85 --preview

# Scan with metrics and alert if >10% dup
duplifinder . --json --dup-threshold 0.1

# Search all occurrences of a class (singleton or multi)
duplifinder . -s class UIManager --preview

# Multiple specs
duplifinder . -s class UIManager -s def dashboard_menu --json

```

Text-pattern mode (find duplicated text by regex):

```bash
# Find duplicated occurrences of lines matching the regex "TODO:"
duplifinder . --pattern-regex "TODO:" --min 2 --json
```

Find specific types/names:

```bash
# Search only for classes
duplifinder . -f class

# Search for a specific definition name
duplifinder . -f "MyClass"

# Mix types and names
duplifinder . -f class -f MyClass
```

## Configuration

Duplifinder reads configuration from the CLI and from a YAML file (path provided via `--config`). CLI arguments take precedence.

Example `.duplifinder.yaml`:
```yaml
root: .
ignore: ".git,__pycache__,venv"
exclude_patterns: "*.pyc,tests/*"
exclude_names: "^_.*,experimental_.*"
find: ["class", "def"]
find_regex: ["class UI.*Manager", "def helper_.*"]
pattern_regex: []
json: false
fail: false
min: 2
verbose: true
parallel: true
use_multiprocessing: false
max_workers: 8
preview: true
```

## CLI reference (common flags)

| Flag | Description |
|------|-------------|
| `<root>` | One or more root paths to scan (default: current dir) |
| `--config <path>` | Path to YAML config file |
| `--ignore` | Comma-separated directory names to ignore (merged with defaults) |
| `--exclude-patterns` | Comma-separated glob patterns for file names to skip |
| `--exclude-names` | Comma-separated regex patterns for definition names to exclude |
| `-f, --find` | Types and names to find (e.g., `class`, `def`, `async_def`, or `MyClass`) |
| `--find-regex` | Regex patterns for types and names (e.g., `class UI.*Manager`) |
| `--pattern-regex` | Regex patterns for duplicate code snippet detection (text mode) |
| `-p, --preview` | Show formatted preview (snippet) of duplicates |
| `--json` | Output as JSON |
| `--fail` | Exit with status code 1 if duplicates were found (useful for CI) |
| `--min` | Minimum occurrences to be considered a duplicate (default: 2) |
| `--verbose` | Verbose logging |
| `--parallel` | Enable parallel file processing |
| `--use-multiprocessing` | Use multiprocessing (ProcessPool) instead of threads |
| `--max-workers` | Max workers when parallel processing is enabled |
| `--version` | Print program version |
| --token-mode | Enable token-based detection for non-definition code blocks |
| --similarity-threshold <float> | Similarity ratio for token dups (0.0-1.0, default: 0.8) |
| --dup-threshold <float> | Duplication rate threshold for alerts (0.0-1.0, default: 0.1) |
| -s, --search <specs> | Search all occurrences of specific definitions (e.g., 'class UIManager'); lists even singles. Requires 'type name'. |

## Output formats

### Console (human)
Nicely formatted listing of duplicate keys (`class <Name>`, `def <Name>`, or pattern match `'<regex>'`) with occurrence counts and optional preview snippets.

Example:
```
class MyClass defined 3 time(s):
  -> /path/to/a.py:10
  -> /path/to/b.py:15
  -> /path/to/c.py:8
```

### JSON (machine)
JSON contains meta information and a structured duplicates object:

```json
{
  "generated_at": "2025-11-01T05:39:50Z",
  "root": "/path/to/repo",
  "scanned_files": 123,
  "skipped_files": ["tests/broken.py"],
  "ignore_dirs": ["__pycache__", ".git"],
  "duplicate_count": 2,
  "duplicates": {
    "class MyClass": [
      {"loc": "/path/to/a.py:10", "snippet": "class MyClass:\n  ...", "type": "class"}
    ],
    "def helper": [
      {"loc": "/path/to/d.py:42", "snippet": "def helper(...):\n  ...", "type": "def"}
    ]
  }
}
```

## Behavior details & implementation notes

- Duplifinder parses Python files using the `ast` module to reliably identify `ClassDef`, `FunctionDef`, and `AsyncFunctionDef`. Methods inside classes are reported as `ClassName.method_name`.
- Text-pattern mode scans file lines for regex matches and collects locations.
- Files matching configured `exclude_patterns` or whose definitions match `exclude_names` are ignored.
- Default ignore set includes common directories: `.git`, `__pycache__`, `.venv`, `venv`, `build`, `dist`, `node_modules`.
- Preview mode uses AST `lineno/end_lineno` to extract contiguous snippet text when available.
- Parallelism: `--parallel` enables concurrent processing; `--use-multiprocessing` switches to `ProcessPoolExecutor` to avoid GIL-bound bottlenecks on large repos (at the cost of process spawn overhead).

## Best practices for usage

- Start with `--preview --min 2 --verbose` to get a human view of what is flagged
- For CI, use `--json + --fail` to programmatically detect regressions
- Use `--exclude-patterns` and `--exclude-names` to tune false positives (e.g., autogenerated files)
- When scanning very large monorepos, experiment with `--max-workers` and `--use-multiprocessing` for throughput

## Development & testing

Recommended dev dependencies: `pytest`, `mypy`, `black`.

Run test suite:
```bash
pip install -e ".[dev]"
pytest -q
```

Lint / format:
```bash
black .
mypy src/duplifinder
```

To run locally as console script:
```bash
python -m duplifinder.main
# or, after editable install:
duplifinder .
```

## Packaging and publishing

The project uses `pyproject.toml` + `setuptools` for packaging. Ensure package metadata (version, authors, URLs) are updated before PyPI release.

```bash
python -m build
twine upload dist/*
```

## Contributing

Contributions are welcome. Please:

1. Open an issue describing the bug or feature
2. Fork the repo, create a branch, and submit a pull request
3. Follow the project's code style and add tests for new behavior
4. Keep changes small and focused; explain rationale in PR description

## Troubleshooting

- **SyntaxError while scanning**: Duplifinder will skip files that cannot be parsed and report them in `skipped_files` (visible in verbose mode or JSON output)
- **Encoding issues**: Ensure source files are UTF-8 or have valid Python encoding declarations
- **False positives**: Use `--exclude-names` or `--exclude-patterns` to filter generated code or private helpers

## License & authors

- License: MIT
- Package version: 2.7.0 (update in `pyproject.toml` as required)
- Author / Maintainers: See `pyproject.toml` and repository metadata

## Contact & references

If you need help, file an issue or create a PR in the repository. The codebase referenced for this README and the CLI options comes from the current project dump.

## Example: common commands summary

```bash
# Full scan, preview duplicates, human output
duplifinder . --preview --verbose

# CI-friendly: JSON output and fail on duplicates
duplifinder . --json --fail

# Text-pattern search (duplicate lines matching regex)
duplifinder . --pattern-regex "FIXME|TODO" --min 3 --json
```
```