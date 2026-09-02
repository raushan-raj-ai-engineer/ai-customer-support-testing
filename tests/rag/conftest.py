from __future__ import annotations

import pytest

from app.rag.chunker import (
    chunk_documents,
)
from app.rag.document_loader import (
    load_knowledge_documents,
)
from app.rag.embedding_service import (
    EmbeddingService,
)
from app.rag.vector_store import (
    PolicyVectorStore,
)


@pytest.fixture(scope="session")
def embedding_service():

    return EmbeddingService()


@pytest.fixture(scope="session")
def policy_vector_store(
    tmp_path_factory,
    embedding_service,
):

    db_path = tmp_path_factory.mktemp("chroma_test_db")

    documents = load_knowledge_documents()

    chunks = chunk_documents(documents)

    store = PolicyVectorStore(
        db_path=db_path,
        collection_name=("test_support_policies"),
        embedding_service=(embedding_service),
    )

    store.index_chunks(
        chunks,
        reset=True,
    )

    return store
