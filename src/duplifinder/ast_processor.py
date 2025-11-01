# src/duplifinder/ast_processor.py

# src/duplifinder/ast_processor.py

"""AST file processor for definition extraction."""

import fnmatch
import logging
import tokenize
import re  # Added for exclude_names
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import ast

from .ast_visitor import EnhancedDefinitionVisitor
from .config import Config


def process_file_ast(py_file: Path, config: Config) -> Tuple[Dict[str, Dict[str, List[Tuple[str, str]]]], str | None, int]:
    """Process a single Python file for definitions using AST; return total_lines."""
    str_py_file = str(py_file)
    if any(fnmatch.fnmatch(py_file.name, pat) for pat in config.exclude_patterns):
        if config.verbose:
            logging.info(f"Skipping {str_py_file}: matches exclude pattern")
        return {}, str_py_file, 0

    total_lines = 0
    try:
        # Encoding-aware open with fallback
        with tokenize.open(py_file) as fh:  # Handles BOM/encoding
            text = fh.read()
        total_lines = len(text.splitlines())
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
        logging.error(f"Skipping {str_py_file} due to parsing error: {type(e).__name__}: {e}", exc_info=config.verbose)
        return {}, str_py_file, 0
    except UnicodeDecodeError as e:
        logging.warning(f"Skipping {str_py_file} due to encoding error: {e}; try --encoding flag in future")
        return {}, str_py_file, 0
    except Exception as e:
        logging.error(f"Skipping {str_py_file}: {type(e).__name__}: {e}", exc_info=config.verbose)
        return {}, str_py_file, 0