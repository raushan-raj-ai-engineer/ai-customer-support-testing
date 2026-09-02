from __future__ import annotations

from app.rag.chunker import (
    chunk_documents,
)
from app.rag.document_loader import (
    load_knowledge_documents,
)
from app.rag.vector_store import (
    PolicyVectorStore,
)


def main() -> None:

    print()
    print("=" * 50)

    print("BUILDING POLICY VECTOR DATABASE")

    print("=" * 50)

    # =====================================================
    # STEP 1
    # LOAD DOCUMENTS
    # =====================================================

    documents = load_knowledge_documents()

    print(f"Documents loaded: {len(documents)}")

    # =====================================================
    # STEP 2
    # SENTENCE-AWARE CHUNKING
    #
    # Important:
    # No chunk_size_words.
    # No overlap_words.
    # =====================================================

    chunks = chunk_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    # =====================================================
    # DEBUG CHUNKS
    # =====================================================

    print()
    print("CHUNKS:")

    for chunk in chunks:
        print(f"[{chunk.chunk_id}] {chunk.content}")

    # =====================================================
    # STEP 3
    # BUILD VECTOR STORE
    # =====================================================

    vector_store = PolicyVectorStore()

    # =====================================================
    # STEP 4
    # RESET + INDEX
    # =====================================================

    indexed = vector_store.index_chunks(
        chunks=chunks,
        reset=True,
    )

    print()
    print(f"Vectors indexed: {indexed}")

    print(f"Collection count: {vector_store.count()}")

    # =====================================================
    # VALIDATION
    # =====================================================

    if vector_store.count() != len(chunks):
        raise RuntimeError(
            "Vector database count does "
            "not match generated chunk count. "
            "Possible stale vector data."
        )

    print()
    print("=" * 50)

    print("VECTOR DATABASE READY")

    print("=" * 50)


if __name__ == "__main__":
    main()
