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