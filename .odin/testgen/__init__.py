"""
ODIN TestGen AI Module v6.0

This module provides automated test generation capabilities for JavaScript/TypeScript 
(via ts-python-parser) and Python (built-in ast) with support for Jest, PyTest, and Luassert.

Features:
- AST parsing for JS/TS and Python
- Edge-case enumeration heuristics
- Multi-framework test renderers
- CLI integration via 'odin testgen'
"""

from .parser import FunctionParser
from .heuristics import EdgeCaseGenerator
from .renderers import TestRenderer
from .core import generate_tests_for_function

__version__ = "6.0.0"
__all__ = ["generate_tests_for_function", "FunctionParser", "EdgeCaseGenerator", "TestRenderer"]
