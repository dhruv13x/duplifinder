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
    mock_config = Mock(search_mode=True, search_specs=["class Foo"])
    with patch("duplifinder.cli.build_config", return_value=mock_config), \
         patch("duplifinder.finder.find_search_matches", return_value=({ "class Foo": [("test.py:1", "snippet")] }, [], 1)), \
         patch("duplifinder.output.render_search"):
        main()
    captured = capsys.readouterr()
    assert "Verified singleton" in captured.out


def test_integration_text_mode(monkeypatch, capsys):
    """Test text pattern mode."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", ".", "--pattern-regex", "TODO"])
    mock_config = Mock(pattern_regexes=["TODO"], search_mode=False, token_mode=False)
    with patch("duplifinder.cli.build_config", return_value=mock_config), \
         patch("duplifinder.finder.find_text_matches", return_value=({ "TODO": ["file:1"] * 2 }, [], 1, 10, 5)), \
         patch("duplifinder.output.render_duplicates"):
        main()
    captured = capsys.readouterr()
    assert "TODO" in captured.out  # Rendered


def test_integration_non_py_skip(monkeypatch):
    """Test non-Py files skipped in discovery."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", str(Path("."))])
    mock_config = Mock(root=Path("."))
    with patch("duplifinder.cli.build_config", return_value=mock_config), \
         patch("duplifinder.utils.discover_py_files", return_value=[]), \
         patch("duplifinder.finder.find_definitions", return_value=({}, ["non_py.py"], 0, 0, 0)):
        main()  # Should run clean, exit 0