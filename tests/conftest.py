# tests/conftest.py

"""Pytest fixtures for Duplifinder."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from src.duplifinder.config import Config
from src.duplifinder.utils import discover_py_files


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
