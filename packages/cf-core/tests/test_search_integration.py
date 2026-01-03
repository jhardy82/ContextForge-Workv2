"""
Integration Test: Semantic Search
Verifies the end-to-end flow: Index -> Embed -> Store -> Search.
"""
import pytest

from cf_core.domain.embedding import Embedding
from cf_core.services.indexing.indexer import CodebaseIndexer
from cf_core.services.search.embedder import LocalEmbedder
from cf_core.services.search.vector_store import DuckDBVectorStore

# Skip if sentence-transformers not installed
try:
    import sentence_transformers
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

@pytest.mark.skipif(not HAS_DEPS, reason="sentence-transformers not installed")
def test_semantic_search_flow():
    # 1. Setup Components
    indexer = CodebaseIndexer()
    embedder = LocalEmbedder()  # uses all-MiniLM-L6-v2
    vector_store = DuckDBVectorStore(db_path=":memory:")

    if not embedder._is_available():
        pytest.skip("Embedder model failed to load")

    # 2. Sample Content (A generic "Velocity" function)
    # We want to search for "speed" and find "velocity".
    sample_code = b"""
def calculate_velocity(distance, time):
    return distance / time

def send_email(to, subject):
    pass
    """

    # 3. Index Content
    nodes = indexer.index_content(file_path="service/physics.py", content=sample_code)
    assert len(nodes) == 2 # Should find 2 functions

    # 4. Embed and Store
    for node in nodes:
        # For this test, we embed "type: name" to give some context
        # In reality, we'd embed docstrings/source code.
        text_to_embed = f"{node.type}: {node.name}"

        vector = embedder.embed(text_to_embed)

        emb = Embedding(
            node_id=node.id,
            vector=vector,
            dimensions=embedder.dimension,
            model_name=embedder.model_name,
            metadata={"file_path": node.file_path, "name": node.name}
        )
        vector_store.add(emb)

    # 5. Search (Vague Query)
    # "compute speed" should map closer to "calculate_velocity" than "send_email"
    query_text = "how to compute speed"
    query_vector = embedder.embed(query_text)

    results = vector_store.search(query_vector, limit=1)

    assert len(results) > 0
    top_node, score = results[0]

    print(f"Query: '{query_text}' -> Match: '{top_node.metadata['name']}' (Score: {score})")

    # Verify we found the right function
    assert "calculate_velocity" in top_node.node_id
    assert top_node.metadata["name"] == "calculate_velocity"
