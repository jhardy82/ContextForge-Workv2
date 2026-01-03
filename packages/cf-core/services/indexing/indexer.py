"""
Codebase Indexer Service
Uses Tree-Sitter to parse source code and extract semantic ContextNodes.
"""
from typing import List

import tree_sitter
import tree_sitter_python
from tree_sitter import Language, Parser

from cf_core.domain.context_node import ContextNode


class CodebaseIndexer:
    """
    Parses Python source code into a semantic graph of ContextNodes.
    """
    def __init__(self):
        # Initialize Tree-Sitter for Python
        # v0.23+ API: Language(ptr)
        self.language = Language(tree_sitter_python.language())
        self.parser = Parser(self.language)

        # Define extraction query
        # We capture the definition node (@def) for range info
        # And the name node (@name) for the identifier
        self.query = self.language.query("""
            (class_definition
                name: (identifier) @class.name
            ) @class.def

            (function_definition
                name: (identifier) @func.name
            ) @func.def

            (import_statement) @import.stmt
            (import_from_statement) @import.from
        """)

    def index_content(self, file_path: str, content: bytes) -> list[ContextNode]:
        """
        Parse content and return discovered ContextNodes.
        """
        tree = self.parser.parse(content)
        cursor = tree_sitter.QueryCursor(self.query)
        matches = cursor.matches(tree.root_node)

        nodes = []

        for match in matches:
            # match is a tuple (match_id, captures_dict)
            # captures_dict is {capture_name: [Node]}
            # match_id is integer

            # v0.25+ binding structure:
            # match = (id, {name: [node, ...]})

            _, captures = match

            if 'class.def' in captures and 'class.name' in captures:
                def_node = captures['class.def'][0]
                name_node = captures['class.name'][0]
                nodes.append(self._create_node(
                    file_path=file_path,
                    node_type='class',
                    name=name_node.text.decode('utf8'),
                    node=def_node
                ))

            elif 'func.def' in captures and 'func.name' in captures:
                def_node = captures['func.def'][0]
                name_node = captures['func.name'][0]
                nodes.append(self._create_node(
                    file_path=file_path,
                    node_type='function',
                    name=name_node.text.decode('utf8'),
                    node=def_node
                ))

            elif 'import.stmt' in captures:
                node = captures['import.stmt'][0]
                nodes.append(self._create_node(
                    file_path=file_path,
                    node_type='import',
                    name="import", # TODO: Extract module names
                    node=node
                ))

            elif 'import.from' in captures:
                node = captures['import.from'][0]
                nodes.append(self._create_node(
                    file_path=file_path,
                    node_type='import',
                    name="import_from", # TODO: Extract module names
                    node=node
                ))

        return nodes

    def _create_node(self, file_path: str, node_type: str, name: str, node) -> ContextNode:
        """Helper to construct ContextNode from Tree-Sitter Node"""
        # Construct unique ID
        # TODO: Handle parent scope in ID for methods (e.g., class.method)
        node_id = f"{file_path}::{node_type}::{name}"
        if node_type == 'import':
             # Imports might need unique IDs based on line number to avoid collisions
             node_id = f"{file_path}::import::{node.start_point[0]}"

        return ContextNode(
            id=node_id,
            type=node_type,
            name=name,
            file_path=file_path,
            start_line=node.start_point[0],
            end_line=node.end_point[0],
            # docstring extraction would happen here
            # complexity calculation would happen here
        )
