"""Integration tests for main flows with exits."""

from unittest.mock import patch, Mock
import sys

import pytest
from duplifinder.main import main


def test_main_default_run(monkeypatch, capsys):
    """Test default run: no dups → exit 0."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", "."])
    with patch("duplifinder.cli.build_config", return_value=Mock(search_mode=False, pattern_regexes=[], token_mode=False)), \
         patch("duplifinder.finder.find_definitions", return_value=({}, [], 1, 10, 0)), \
         patch("duplifinder.output.render_duplicates"):
        main()
    captured = capsys.readouterr()
    assert "No duplicates found" in captured.out


def test_main_config_error(monkeypatch):
    """Test invalid config → exit 2."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", ".", "--pattern-regex", "[invalid"])
    with patch("duplifinder.cli.build_config", side_effect=SystemExit(2)):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2


def test_main_scan_fail_high_skips(monkeypatch):
    """Test >10% skips → exit 3."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", "."])
    mock_config = Mock(search_mode=False, pattern_regexes=[], token_mode=False)
    with patch("duplifinder.cli.build_config", return_value=mock_config), \
         patch("duplifinder.finder.find_definitions", return_value=({}, ["skipped1.py", "skipped2.py"], 1, 10, 0)), \
         patch("duplifinder.output.render_duplicates"):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 3  # High skip rate


def test_main_fail_on_dups(monkeypatch):
    """Test dups with --fail → exit 1."""
    monkeypatch.setattr(sys, "argv", ["duplifinder", ".", "--fail"])
    mock_config = Mock(fail_on_duplicates=True, search_mode=False)
    with patch("duplifinder.cli.build_config", return_value=mock_config), \
         patch("duplifinder.finder.find_definitions", return_value=({ "class Dup": { "Dup": [("file:1", "")] * 2 } }, [], 1, 10, 5)), \
         patch("duplifinder.output.render_duplicates"):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1