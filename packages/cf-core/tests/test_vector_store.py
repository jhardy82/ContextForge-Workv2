"""
Tests for DuckDB Vector Store
"""

import os

import pytest

from cf_core.domain.embedding import Embedding
from cf_core.services.search.vector_store import DuckDBVectorStore


@pytest.fixture
def vector_store():
    store = DuckDBVectorStore(db_path=":memory:")
    return store


def test_add_and_get_embedding(vector_store):
    emb = Embedding(
        node_id="test_node_1",
        vector=[0.1, 0.2, 0.3],
        dimensions=3,
        model_name="test_model",
        metadata={"foo": "bar"},
    )
    vector_store.add(emb)

    retrieved = vector_store.get("test_node_1")
    assert retrieved is not None
    assert retrieved.node_id == "test_node_1"
    assert retrieved.vector == pytest.approx([0.1, 0.2, 0.3])
    assert retrieved.metadata["foo"] == "bar"


def test_vector_search(vector_store):
    # Create 3 vectors
    # Target: [1, 0, 0]
    # Close: [0.9, 0.1, 0]
    # Far: [0, 1, 0]

    vec_target = [1.0, 0.0, 0.0]
    vec_close = [0.9, 0.1, 0.0]
    vec_far = [0.0, 1.0, 0.0]

    vector_store.add(
        Embedding(node_id="target", vector=vec_target, dimensions=3, model_name="test")
    )
    vector_store.add(Embedding(node_id="close", vector=vec_close, dimensions=3, model_name="test"))
    vector_store.add(Embedding(node_id="far", vector=vec_far, dimensions=3, model_name="test"))

    # Search for [1, 0, 0]
    results = vector_store.search([1.0, 0.0, 0.0], limit=2)

    assert len(results) == 2
    top_node, top_score = results[0]
    second_node, second_score = results[1]

    assert top_node.node_id == "target"
    # Cosine sim of identical is 1.0
    assert top_score > 0.99

    assert second_node.node_id == "close"
    # Cosine sim of [1,0,0] and [0.9,0.1,0]
    # 0.9 / (1 * sqrt(0.81+0.01)) = 0.9 / 0.9055 = ~0.99
    assert second_score > 0.8  # Far is 0.0
