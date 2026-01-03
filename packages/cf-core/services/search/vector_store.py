"""
DuckDB Vector Store
Implements vector storage and similarity search using DuckDB.
"""
import json
from typing import List, Optional, Tuple

import duckdb

from cf_core.domain.embedding import Embedding


class DuckDBVectorStore:
    """
    Persists embeddings in a DuckDB table and performs vector similarity search.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.conn = duckdb.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        """Create the embeddings table if it doesn't exist."""
        # We store vectors as FLOAT[] (array)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                node_id VARCHAR PRIMARY KEY,
                vector FLOAT[],
                dimensions INTEGER,
                model_name VARCHAR,
                metadata JSON
            )
        """)
        # Install vss extension if available?
        # For simple implementations, raw array ops are fine for small K.
        # But we can try to load it.
        try:
            self.conn.execute("INSTALL vss; LOAD vss;")
        except Exception:
            # Fallback to standard array functions if VSS not available
            pass

    def add(self, embedding: Embedding):
        """Upsert an embedding."""
        # DuckDB upsert syntax: INSERT OR REPLACE
        self.conn.execute("""
            INSERT OR REPLACE INTO embeddings
            (node_id, vector, dimensions, model_name, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            embedding.node_id,
            embedding.vector,
            embedding.dimensions,
            embedding.model_name,
            json.dumps(embedding.metadata)
        ))

    def search(self, query_vector: list[float], limit: int = 5) -> list[tuple[Embedding, float]]:
        """
        Find specific embeddings similar to the query vector.
        Returns List of (Embedding, score).
        """
        # Cosine Similarity using array_cosine_similarity (if vss) or manual calculation
        # DuckDB native: list_cosine_similarity(a, b) available in recent versions?
        # Let's assume standard SQL math if function missing, but list_cosine_similarity is standard in recent DuckDB.

        # We'll try the native list_cosine_similarity function first.
        try:
             results = self.conn.execute("""
                SELECT
                    node_id, vector, dimensions, model_name, metadata,
                    list_cosine_similarity(vector, CAST(? AS FLOAT[])) as score
                FROM embeddings
                ORDER BY score DESC
                LIMIT ?
            """, (query_vector, limit)).fetchall()
        except duckdb.BinderException:
             # Fallback if list_cosine_similarity not found (older versions)
             # Manual cosine similarity: (A . B) / (|A| * |B|)
             # This is slow, but functional for small datasets.
             # Ideally we rely on recent DuckDB.
             raise NotImplementedError("DuckDB version too old, missing list_cosine_similarity")

        output = []
        for row in results:
            node_id, vector, dimensions, model_name, meta_json, score = row
            emb = Embedding(
                node_id=node_id,
                vector=vector,
                dimensions=dimensions,
                model_name=model_name,
                metadata=json.loads(meta_json) if meta_json else {}
            )
            output.append((emb, score))

        return output

    def get(self, node_id: str) -> Embedding | None:
        """Retrieve by ID."""
        row = self.conn.execute("""
            SELECT node_id, vector, dimensions, model_name, metadata
            FROM embeddings
            WHERE node_id = ?
        """, (node_id,)).fetchone()

        if not row:
            return None

        return Embedding(
            node_id=row[0],
            vector=row[1],
            dimensions=row[2],
            model_name=row[3],
            metadata=json.loads(row[4]) if row[4] else {}
        )
