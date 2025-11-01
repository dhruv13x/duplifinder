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