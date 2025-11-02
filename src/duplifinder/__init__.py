# src/duplifinder/__init__.py

"""Duplifinder: Detect duplicate Python definitions across projects."""

__version__ = "6.0.2"

from . import main  # For entrypoint
from .config import Config
from .ast_visitor import EnhancedDefinitionVisitor

__all__ = ["Config", "EnhancedDefinitionVisitor", "main"]
