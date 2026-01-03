"""
Spike: Verify Tree-Sitter Parsing
Usage: pip install tree-sitter tree-sitter-python && python spike_treesitter.py
"""

import tree_sitter
import tree_sitter_python
from tree_sitter import Language, Parser


def test_parsing():
    # 1. Load Grammar
    PY_LANGUAGE = Language(tree_sitter_python.language())

    # 2. Init Parser
    parser = Parser(PY_LANGUAGE)
    # parser.set_language(PY_LANGUAGE) - Removed in 0.22+

    # 3. Parse Self
    with open(__file__, "rb") as f:
        src = f.read()

    tree = parser.parse(src)
    root = tree.root_node

    print(f"Root Type: {root.type}")
    print(f"Child Count: {root.child_count}")

    # 4. Query for Function Definitions
    query = PY_LANGUAGE.query("""
    (function_definition
      name: (identifier) @func.name)
    """)

    print(f"tree_sitter content: {dir(tree_sitter)}")

    if hasattr(tree_sitter, "QueryCursor"):
        try:
            # Try passing query to constructor if it demands it
            cursor = tree_sitter.QueryCursor(query)
            print(f"QueryCursor methods: {dir(cursor)}")
            # Try matches
            if hasattr(cursor, "matches"):
                print("Trying cursor.matches(root)...")
                try:
                    matches = cursor.matches(root)
                    print(f"Matches object: {matches} (Type: {type(matches)})")

                    # Iterate matches
                    count = 0
                    for match in matches:
                        print(f"Match: {match} (Type: {type(match)})")
                        print(f"Match attributes: {dir(match)}")
                        count += 1
                        if count > 2:
                            break
                except Exception as e:
                    print(f"matches(root) failed: {e}")

            elif hasattr(cursor, "captures"):
                pass  # Already tried
            else:
                # In some bindings, it's cursor.exec(query, node)? No, constructor took query.
                # Maybe it's an iterator itself?
                captures = list(cursor)
                pass

            # If captures is a dict or list?
            if not isinstance(captures, (list, tuple)):
                # It might be an iterator
                captures = list(captures)

        except TypeError as e:
            print(f"QueryCursor init failed: {e}")
            # Try without arg again just in case (though error said otherwise)
            cursor = tree_sitter.QueryCursor()
    else:
        print("QueryCursor not found in tree_sitter module")
        return

    print(f"Captures object: {captures} (Type: {type(captures)})")

    if isinstance(captures, dict):
        for name, nodes in captures.items():
            print(f"Capture Name: {name}")
            if isinstance(nodes, list):
                for node in nodes:
                    print(
                        f" - Node Type: {node.type}, Text: {src[node.start_byte : node.end_byte].decode('utf8').splitlines()[0]}"
                    )
            else:
                print(f" - Node: {nodes}")
    else:
        # Fallback inspection
        pass

    # captures = query.captures(root)
    print(
        f"Found {len(captures) if isinstance(captures, list) else 'unknown'} captures (Iterating...)"
    )
    for item in captures:
        print(f"Capture Item: {item} (Type: {type(item)})")
        # Try to inspect structure
        # In new bindings, it might be a Capture object or tuple
        if isinstance(item, tuple):
            print(f"Tuple len: {len(item)}")

        # for node, name in captures: -> Original code
        # print(f" - {src[node.start_byte : node.end_byte].decode('utf8')}")


if __name__ == "__main__":
    test_parsing()
