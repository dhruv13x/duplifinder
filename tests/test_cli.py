# tests/test_cli.py

"""Tests for CLI parsing and config building."""

import argparse
import pathlib
from unittest.mock import patch

import pytest
from duplifinder.cli import create_parser, build_config, validate_config
from duplifinder.config import Config, DEFAULT_IGNORES


def test_create_parser_help(capsys):
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(['--help'])
    captured = capsys.readouterr()
    assert 'Find duplicate Python definitions' in captured.out


def test_build_config_defaults():
    args = argparse.Namespace(
        root=['.'], verbose=False, ignore='', exclude_patterns='', exclude_names='',
        find=[], find_regex=[], pattern_regex=[], search=[], token_mode=False,
        similarity_threshold=0.8, dup_threshold=0.1, json=False, fail=False, min=2,
        parallel=False, use_multiprocessing=False, max_workers=None, preview=False, config=None
    )
    config_dict = {}
    with patch('duplifinder.cli.logging') as mock_logging:
        config = build_config(args, config_dict)
    assert config.root == pathlib.Path('.').resolve()
    assert config.ignore_dirs == DEFAULT_IGNORES
    assert config.types_to_search == {'class', 'def', 'async_def'}
    assert not config.search_mode


def test_build_config_with_search():
    args = argparse.Namespace(
        root=[], verbose=True, ignore='', exclude_patterns='', exclude_names='',
        find=[], find_regex=[], pattern_regex=[], search=['class UIManager'], token_mode=False,
        similarity_threshold=0.8, dup_threshold=0.1, json=False, fail=False, min=2,
        parallel=False, use_multiprocessing=False, max_workers=None, preview=False, config=None
    )
    config_dict = {}
    with patch('duplifinder.cli.logging'):
        config = build_config(args, config_dict)
    assert config.search_mode is True
    assert config.search_specs == ['class UIManager']


def test_validate_config_search_guard():
    parser = argparse.ArgumentParser()
    config = Config(
        root=pathlib.Path('.'), ignore_dirs=set(), exclude_patterns=set(), exclude_names=set(),
        types_to_search=set(), filter_names=set(), filter_regexes=[], pattern_regexes=[],
        search_specs=['class'], search_mode=True, token_mode=False, similarity_threshold=0.8,
        dup_threshold=0.1, json_output=False, fail_on_duplicates=False, min_occurrences=2,
        verbose=False, parallel=False, use_multiprocessing=False, max_workers=None, preview=False
    )
    with pytest.raises(SystemExit):
        validate_config(config, parser)  # Bare 'class' invalid


def test_validate_config_invalid_threshold():
    parser = argparse.ArgumentParser()
    config = Config(
        root=pathlib.Path('.'), ignore_dirs=set(), exclude_patterns=set(), exclude_names=set(),
        types_to_search=set(), filter_names=set(), filter_regexes=[], pattern_regexes=[],
        search_specs=[], search_mode=False, token_mode=False, similarity_threshold=1.5,
        dup_threshold=0.1, json_output=False, fail_on_duplicates=False, min_occurrences=2,
        verbose=False, parallel=False, use_multiprocessing=False, max_workers=None, preview=False
    )
    with pytest.raises(SystemExit):
        validate_config(config, parser)