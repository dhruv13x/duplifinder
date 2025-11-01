# tests/test_output.py

"""Tests for output rendering."""

from unittest.mock import patch, Mock
import json

import pytest
from duplifinder.output import render_duplicates, render_search, render_search_json
from duplifinder.config import Config
from pathlib import Path


def test_render_duplicates_empty(capsys):
    config = Mock(spec=Config, preview=False)
    render_duplicates({}, config, False, 0.0, 0.1, 0, 0)
    captured = capsys.readouterr()
    assert 'No duplicates found' in captured.out


def test_render_search_singleton(capsys):
    config = Mock(spec=Config, preview=False)
    results = {'class UIManager': [('file.py:1', 'snippet')]}
    render_search(results, config)
    captured = capsys.readouterr()
    assert 'Verified singleton' in captured.out
    assert 'file.py:1' in captured.out


def test_render_search_json():
    config = Mock(spec=Config)
    config.root = Path('.')
    results = {'class UIManager': [('file.py:1', 'snippet')]}
    with patch('sys.stdout') as mock_stdout:
        render_search_json(results, config, 1, [])
    output = mock_stdout.write.call_args.args[0]
    parsed = json.loads(output)
    assert parsed['search_results']['class UIManager']['is_singleton'] is True
    assert len(parsed['search_results']['class UIManager']['occurrences']) == 1


def test_render_duplicates_with_metrics(capsys):
    config = Mock(spec=Config, dup_threshold=0.1)
    render_duplicates({}, config, False, 0.15, 0.1, 100, 15)
    captured = capsys.readouterr()
    assert 'ALERT: Duplication rate' in captured.out  # Threshold exceeded