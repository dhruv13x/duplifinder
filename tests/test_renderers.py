"""Tests for renderers."""

import json
from unittest.mock import patch

import pytest
from duplifinder.duplicate_renderer import render_duplicates
from duplifinder.search_renderer import render_search, render_search_json
from duplifinder.config import Config


def test_render_duplicates_empty(capsys, mock_config):
    """Test empty dups show 'No duplicates'."""
    mock_config.json_output = False
    render_duplicates({}, mock_config, False, 0.0, 0.1, 0, 0)
    captured = capsys.readouterr()
    assert "No duplicates found" in captured.out


def test_render_duplicates_alert(capsys, mock_config):
    """Test dup rate alert."""
    mock_config.dup_threshold = 0.1
    mock_config.json_output = False
    render_duplicates({}, mock_config, False, 0.15, 0.1, 100, 15)
    captured = capsys.readouterr()
    assert "ALERT: Duplication rate" in captured.out


def test_render_search_singleton(capsys, mock_config):
    """Test singleton search output."""
    mock_config.json_output = False
    results = {"class Foo": [("file.py:1", "snippet")]}
    render_search(results, mock_config)
    captured = capsys.readouterr()
    assert "Verified singleton" in captured.out


def test_render_search_json(mock_config):
    """Test JSON search output."""
    mock_config.root = Path(".")
    results = {"class Foo": [("file.py:1", "snippet")]}
    with patch("sys.stdout") as mock_stdout:
        render_search_json(results, mock_config, 1, [])
    output = mock_stdout.write.call_args.args[0]
    parsed = json.loads(output)
    assert parsed["search_results"]["class Foo"]["is_singleton"] is True


def test_render_duplicates_token_mode(capsys, mock_config):
    """Test token rendering normalization."""
    mock_config.json_output = False
    token_results = {"token similarity >80%": [("file:1:2 ~ file:3:4 (sim: 0.85)", "", 0.85)]}
    render_duplicates(token_results, mock_config, False, 0.0, 0.1, 10, 0, is_token=True)
    captured = capsys.readouterr()
    assert "(sim: 0.85)" in captured.out  # Normalized