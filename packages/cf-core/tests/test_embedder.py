"""
Tests for Local Embedder
"""

import pytest

from cf_core.services.search.embedder import LocalEmbedder

# Skip if sentence-transformers not installed
try:
    import sentence_transformers

    HAS_DEPS = True
except ImportError as e:
    HAS_DEPS = False
    IMPORT_ERROR = str(e)
except Exception as e:
    HAS_DEPS = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(
    not HAS_DEPS,
    reason=f"sentence-transformers not installed: {globals().get('IMPORT_ERROR', 'Unknown error')}",
)
def test_embed_single_string():
    embedder = LocalEmbedder()  # Use default model
    if not embedder._is_available():
        pytest.skip("Model failed to load")

    text = "This is a test function."
    vector = embedder.embed(text)

    assert isinstance(vector, list)
    assert len(vector) == 384  # Default model dimension
    assert all(isinstance(x, float) for x in vector)


@pytest.mark.skipif(not HAS_DEPS, reason="sentence-transformers not installed")
def test_embed_batch():
    embedder = LocalEmbedder()
    if not embedder._is_available():
        pytest.skip("Model failed to load")

    texts = ["Function A", "Function B"]
    vectors = embedder.embed_batch(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) == 384
