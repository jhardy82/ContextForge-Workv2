"""
Local Embedder Service
Uses sentence-transformers to generate embeddings locally.
"""
import logging
from typing import List

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

logger = logging.getLogger(__name__)

class LocalEmbedder:
    """
    Wrapper around SentenceTransformer for local embedding generation.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

        if not HAS_SENTENCE_TRANSFORMERS:
            logger.warning("sentence-transformers not installed. Semantic search will be disabled.")
            return

        try:
            logger.info(f"Loading embedding model: {model_name}")
            self._model = SentenceTransformer(model_name)
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self._model = None

    def embed(self, text: str) -> list[float]:
        """
        Generate embedding vector for a single string.
        """
        if not self._is_available():
            raise RuntimeError("Embedding model not available. Install 'sentence-transformers'.")

        vector = self._model.encode(text)
        return vector.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of strings.
        """
        if not self._is_available():
            raise RuntimeError("Embedding model not available.")

        vectors = self._model.encode(texts)
        return vectors.tolist()

    def _is_available(self) -> bool:
        return HAS_SENTENCE_TRANSFORMERS and self._model is not None

    @property
    def dimension(self) -> int:
        """Return the dimension of the embeddings (e.g. 384)."""
        if self._is_available():
            return self._model.get_sentence_embedding_dimension()
        return 0
