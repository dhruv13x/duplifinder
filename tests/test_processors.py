"""Tests for processors with edges."""

import re
from pathlib import Path

import pytest
from duplifinder.ast_processor import process_file_ast
from duplifinder.text_processor import process_file_text
from duplifinder.token_processor import process_file_tokens, tokenize_block
from duplifinder.config import Config
from duplifinder.processor_utils import estimate_dup_lines


def test_process_file_ast_valid(sample_py_file, mock_config):
    """Test AST processing on valid file."""
    defs, skipped, lines = process_file_ast(sample_py_file, mock_config)
    assert skipped is None
    assert lines == 6
    assert "class" in defs
    assert "SingletonClass" in defs["class"]


def test_process_file_ast_invalid(invalid_py_file, mock_config):
    """Test AST skips syntax errors."""
    defs, skipped, lines = process_file_ast(invalid_py_file, mock_config)
    assert skipped == str(invalid_py_file)
    assert lines == 0


def test_process_file_ast_exclude(mock_config, sample_py_file):
    """Test exclude_patterns skips files."""
    mock_config.exclude_patterns = {"test.py"}
    defs, skipped, lines = process_file_ast(sample_py_file, mock_config)
    assert skipped == str(sample_py_file)


def test_process_file_ast_exclude_names(mock_config, sample_py_file):
    """Test exclude_names filters defs."""
    mock_config.exclude_names = {"Singleton.*"}
    defs, skipped, lines = process_file_ast(sample_py_file, mock_config)
    assert "SingletonClass" not in defs["class"]  # Filtered


def test_tokenize_block():
    """Test tokenization normalizes."""
    text = "def foo(): pass  # comment"
    tokens = tokenize_block(text)
    assert "def" in tokens
    assert "foo" in tokens
    assert "# comment" not in " ".join(tokens)


def test_process_file_text_match(sample_py_file, mock_config):
    """Test text pattern matching."""
    patterns = [re.compile("class")]
    matches, skipped, lines = process_file_text(sample_py_file, patterns, mock_config)
    assert skipped is None
    assert "class" in matches
    assert len(matches["class"]) == 1


def test_process_file_text_no_match(tmp_path: Path, mock_config):
    """Test no matches returns empty."""
    py_file = tmp_path / "no_match.py"
    py_file.write_text("No class here")
    patterns = [re.compile("class")]
    matches, skipped, lines = process_file_text(py_file, patterns, mock_config)
    assert matches == {}


def test_process_file_tokens_similarity(tmp_path: Path, mock_config):
    """Test token similarity detection."""
    mock_config.similarity_threshold = 0.5
    py_file = tmp_path / "similar.py"
    py_file.write_text("def sim1(): pass\ndef sim2(): pass")
    similarities, skipped, lines = process_file_tokens(py_file, mock_config)
    assert skipped is None
    assert "token similarity >50%" in similarities


def test_estimate_dup_lines_below_min(mock_config):
    """Test dup estimation < min_occurrences = 0."""
    items = [("loc1", "")]
    assert estimate_dup_lines(items, False, mock_config) == 0


def test_estimate_dup_lines_above_min(mock_config, sample_py_file):
    """Test dup estimation > min."""
    mock_config.min_occurrences = 1
    items = [("loc1", ""), ("loc2", "")]
    assert estimate_dup_lines(items, False, mock_config) > 0