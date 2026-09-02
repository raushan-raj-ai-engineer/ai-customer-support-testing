from __future__ import annotations

from functools import lru_cache
from typing import cast

import numpy as np
from chromadb.api.types import (
    Embedding,
    Embeddings,
)
from sentence_transformers import (
    SentenceTransformer,
)

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=2)
def _load_model(
    model_name: str,
) -> SentenceTransformer:

    return SentenceTransformer(model_name)


class EmbeddingService:
    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:

        self.model_name = model_name

        self.model = _load_model(model_name)

    # =====================================================
    # DOCUMENT EMBEDDINGS
    # =====================================================

    def embed_documents(
        self,
        texts: list[str],
    ) -> Embeddings:

        if not texts:
            return []

        raw_embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        array = np.asarray(
            raw_embeddings,
            dtype=np.float32,
        )

        embeddings = [
            np.asarray(
                row,
                dtype=np.float32,
            )
            for row in array
        ]

        return cast(
            Embeddings,
            embeddings,
        )

    # =====================================================
    # QUERY EMBEDDING
    # =====================================================

    def embed_query(
        self,
        query: str,
    ) -> Embedding:

        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty")

        raw_embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        embedding = np.asarray(
            raw_embedding,
            dtype=np.float32,
        )

        return cast(
            Embedding,
            embedding,
        )
