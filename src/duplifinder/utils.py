# src/duplifinder/utils.py

"""Shared utilities for file discovery and parallel execution."""

import concurrent.futures
import contextlib
import logging
import os
import mimetypes
from pathlib import Path
from typing import Callable, Generator, List, Any

from tqdm import tqdm

from .config import Config


def discover_py_files(config: Config) -> List[Path]:
    """Discover Python files, excluding ignored dirs and non-Py content."""
    candidates = [
        p for p in config.root.rglob("*.py")
        if not any(part in config.ignore_dirs for part in p.parts)
    ]
    py_files = []
    for p in candidates:
        # Check MIME/content for non-Py masqueraders
        mime, _ = mimetypes.guess_type(str(p))
        if mime != "text/x-python":
            logging.warning(f"Skipping non-Py file '{p}': MIME {mime}")
            continue
        # Quick content check (first 1024 bytes)
        try:
            with open(p, "rb") as f:
                header = f.read(1024)
                if not (header.startswith(b"#!") or b"def " in header or b"class " in header):
                    logging.warning(f"Skipping non-Py content '{p}': No Python markers")
                    continue
        except Exception:
            pass  # Assume Py if unreadable
        py_files.append(p)
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
            futures = [executor.submit(process_fn, p, *args, config=config, **kwargs) for p in py_files]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(py_files), disable=not config.verbose, desc="Processing files"):
                yield future.result()
        else:
            for py_file in tqdm(py_files, disable=not config.verbose, desc="Processing files"):
                yield process_fn(py_file, *args, config=config, **kwargs)


def log_file_count(py_files: List[Path], config: Config, context: str = "process") -> None:
    """Log the number of files discovered."""
    if config.verbose:
        logging.info(f"Found {len(py_files)} Python files to {context}.")