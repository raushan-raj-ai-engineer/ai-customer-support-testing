from __future__ import annotations

import re

from app.rag.models import (
    DocumentChunk,
    KnowledgeDocument,
)

# =========================================================
# MARKDOWN CLEANING
# =========================================================


def _remove_markdown_headings(
    content: str,
) -> str:
    """
    Remove Markdown heading lines.

    Example:

        # Shipping Policy

    We already store the policy title separately in
    metadata, so the heading does not need to become
    part of the embedding text.
    """

    cleaned_lines: list[str] = []

    for line in content.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        cleaned_lines.append(stripped)

    return " ".join(cleaned_lines)


# =========================================================
# SENTENCE SPLITTING
# =========================================================


def split_into_sentences(
    content: str,
) -> list[str]:
    """
    Split policy text into complete sentences.

    We intentionally avoid word-count chunking because
    it can produce fragments such as:

        "Customers receive a tracking"

    Atomic sentences provide much cleaner RAG context
    for these small policy documents.
    """

    cleaned = _remove_markdown_headings(content)

    if not cleaned:
        return []

    raw_sentences = re.split(
        r"(?<=[.!?])\s+",
        cleaned,
    )

    sentences: list[str] = []

    for sentence in raw_sentences:
        normalized = sentence.strip()

        if not normalized:
            continue

        sentences.append(normalized)

    return sentences


# =========================================================
# CHUNK ONE DOCUMENT
# =========================================================


def chunk_document(
    document: KnowledgeDocument,
) -> list[DocumentChunk]:
    """
    Create one atomic chunk per complete policy sentence.

    Example:

        Chunk 0:
        "Standard shipping normally takes
        3 to 5 business days."

        Chunk 1:
        "Express shipping normally takes
        1 to 2 business days."

    This is intentional for our small policy knowledge base.
    """

    sentences = split_into_sentences(document.content)

    chunks: list[DocumentChunk] = []

    for chunk_index, sentence in enumerate(sentences):
        chunk_id = f"{document.policy_id.lower()}-chunk-{chunk_index:03d}"

        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                policy_id=(document.policy_id),
                title=(document.title),
                source=(document.source),
                chunk_index=(chunk_index),
                content=sentence,
            )
        )

    return chunks


# =========================================================
# CHUNK ALL DOCUMENTS
# =========================================================


def chunk_documents(
    documents: list[KnowledgeDocument],
) -> list[DocumentChunk]:

    chunks: list[DocumentChunk] = []

    for document in documents:
        chunks.extend(chunk_document(document))

    return chunks
