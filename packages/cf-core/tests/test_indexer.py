"""
Tests for CodebaseIndexer
"""
import pytest

from cf_core.domain.context_node import ContextNode
from cf_core.services.indexing.indexer import CodebaseIndexer

SAMPLE_CODE = b"""
import os
from typing import List

class MyClass:
    def my_method(self):
        pass

def global_function():
    return True
"""

def test_indexer_extracts_entities():
    indexer = CodebaseIndexer()
    nodes = indexer.index_content("test_file.py", SAMPLE_CODE)

    # Check Import
    imports = [n for n in nodes if n.type == 'import']
    assert len(imports) >= 2

    # Check Class
    classes = [n for n in nodes if n.type == 'class']
    assert len(classes) == 1
    assert classes[0].name == "MyClass"
    assert classes[0].start_line == 4

    # Check Function
    funcs = [n for n in nodes if n.type == 'function']
    # Note: my_method is inside class, currently flattened or caught as function type
    # Our query separates them, but logic appends both.

    global_func = next(n for n in funcs if n.name == "global_function")
    assert global_func.start_line == 8

    method_func = next(n for n in funcs if n.name == "my_method")
    assert method_func.start_line == 5
