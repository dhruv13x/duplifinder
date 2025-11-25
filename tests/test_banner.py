# tests/test_banner.py

"""Tests for the banner logo."""

import os
from unittest.mock import patch, MagicMock

from duplifinder.banner import print_logo


@patch("duplifinder.banner.console")
def test_print_logo_procedural(mock_console: MagicMock):
    """Test logo prints with a procedurally generated palette."""
    print_logo()
    assert mock_console.print.call_count > 10  # Logo + tagline


@patch("duplifinder.banner.console")
def test_print_logo_fixed_palette(mock_console: MagicMock):
    """Test logo prints with a fixed palette from an environment variable."""
    with patch.dict(os.environ, {"CREATE_DUMP_PALETTE": "1"}):
        print_logo()
    assert mock_console.print.call_count > 10


@patch("duplifinder.banner.console")
def test_print_logo_invalid_palette_index(mock_console: MagicMock):
    """Test that an out-of-bounds palette index falls back to procedural."""
    with patch.dict(os.environ, {"CREATE_DUMP_PALETTE": "999"}):
        print_logo()
    assert mock_console.print.call_count > 10


@patch("duplifinder.banner.console")
def test_print_logo_invalid_palette_value(mock_console: MagicMock):
    """Test that a non-integer palette value falls back to procedural."""
    with patch.dict(os.environ, {"CREATE_DUMP_PALETTE": "abc"}):
        print_logo()
    assert mock_console.print.call_count > 10
