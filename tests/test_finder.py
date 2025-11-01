# tests/test_finder.py

"""Tests for finder logic."""

from pathlib import Path
from unittest.mock import patch

import pytest
from duplifinder.finder import discover_py_files, find_search_matches
from duplifinder.config import Config


def test_discover_py_files(tmp_path):
    (tmp_path / 'a.py').touch()
    (tmp_path / 'b.txt').touch()
    (tmp_path / '.git').mkdir()  # Create dir first
    (tmp_path / '.git' / 'c.py').touch()
    config = Config(
        root=tmp_path, ignore_dirs={'.git'}, exclude_patterns=set(), exclude_names=set(),
        types_to_search={'class'}, filter_names=set(), filter_regexes=[], pattern_regexes=[],
        search_specs=[], search_mode=False, token_mode=False, similarity_threshold=0.8,
        dup_threshold=0.1, json_output=False, fail_on_duplicates=False, min_occurrences=2,
        verbose=False, parallel=False, use_multiprocessing=False, max_workers=None, preview=False
    )
    files = discover_py_files(config)
    assert len(files) == 1
    assert files[0].name == 'a.py'  # Ignores .git/c.py


@patch('duplifinder.finder.run_parallel')
def test_find_search_matches(mock_run, tmp_path):
    sample_file = tmp_path / 'test.py'
    sample_file.write_text('class UIManager:\n    pass')
    config = Config(
        root=tmp_path, ignore_dirs=set(), exclude_patterns=set(), exclude_names=set(),
        types_to_search={'class'}, filter_names=set(), filter_regexes=[], pattern_regexes=[],
        search_specs=['class UIManager'], search_mode=True, token_mode=False, similarity_threshold=0.8,
        dup_threshold=0.1, json_output=False, fail_on_duplicates=False, min_occurrences=2,
        verbose=False, parallel=False, use_multiprocessing=False, max_workers=None, preview=True
    )
    mock_defs = ({'class': {'UIManager': [('test.py:1', 'snippet')]}}, None, 4)
    mock_run.return_value = [mock_defs]
    results, skipped, scanned = find_search_matches(config)
    assert scanned == 1
    assert 'class UIManager' in results
    assert len(results['class UIManager']) == 1