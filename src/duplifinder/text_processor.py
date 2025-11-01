# src/duplifinder/text_processor.py

"""Text file processor for regex pattern matching."""

import fnmatch
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Tuple
from .config import Config


def process_file_text(py_file: Path, patterns: List[re.Pattern], config: Config) -> Tuple[Dict[str, List[str]], str | None, int]:
    """Process a single Python file for text patterns; return total_lines."""
    str_py_file = str(py_file)
    if any(fnmatch.fnmatch(py_file.name, pat) for pat in config.exclude_patterns):
        if config.verbose:
            logging.info(f"Skipping {str_py_file}: matches exclude pattern")
        return {}, str_py_file, 0

    total_lines = 0
    try:
        # Encoding-aware open
        with open(py_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        total_lines = len(lines)
        matches: Dict[str, List[str]] = defaultdict(list)
        for lineno, line in enumerate(lines, 1):
            for pat in patterns:
                if pat.search(line):
                    matches[pat.pattern].append(f"{str_py_file}:{lineno}")
        return matches, None, total_lines
    except UnicodeDecodeError as e:
        logging.warning(f"Skipping {str_py_file} due to encoding error: {e}")
        return {}, str_py_file, 0
    except Exception as e:
        logging.error(f"Skipping {str_py_file}: {type(e).__name__}: {e}", exc_info=config.verbose)
        return {}, str_py_file, 0