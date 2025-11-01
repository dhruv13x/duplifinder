# src/duplifinder/ast_visitor.py

"""AST visitor for collecting Python definitions."""

import ast
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from .config import KNOWN_TYPES


class EnhancedDefinitionVisitor(ast.NodeVisitor):
    """AST visitor to collect definitions and method names within classes."""

    def __init__(self, types_to_search: Set[str]) -> None:
        self.definitions: Dict[str, List[Tuple[str, int, int, str]]] = defaultdict(list)
        self.types_to_search = types_to_search

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if "class" in self.types_to_search:
            end_lineno = node.end_lineno if node.end_lineno is not None else node.lineno
            self.definitions["class"].append((node.name, node.lineno, end_lineno, ""))
        # Collect method names within classes
        if "def" in self.types_to_search or "async_def" in self.types_to_search:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    t = "def" if isinstance(item, ast.FunctionDef) else "async_def"
                    if t in self.types_to_search:
                        end_lineno = item.end_lineno if item.end_lineno is not None else item.lineno
                        self.definitions[t].append((f"{node.name}.{item.name}", item.lineno, end_lineno, ""))
        self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        for t in self.types_to_search:
            if isinstance(node, KNOWN_TYPES[t]) and not isinstance(node, ast.ClassDef):
                end_lineno = node.end_lineno if node.end_lineno is not None else node.lineno
                self.definitions[t].append((node.name, node.lineno, end_lineno, ""))
        super().generic_visit(node)
