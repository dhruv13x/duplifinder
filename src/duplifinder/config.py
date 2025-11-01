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