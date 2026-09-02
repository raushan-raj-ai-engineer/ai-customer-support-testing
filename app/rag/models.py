from __future__ import annotations

from dataclasses import dataclass

# =========================================================
# SOURCE DOCUMENT
# =========================================================


@dataclass(frozen=True)
class KnowledgeDocument:
    policy_id: str
    title: str
    source: str
    content: str


# =========================================================
# DOCUMENT CHUNK
# =========================================================


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    policy_id: str
    title: str
    source: str
    chunk_index: int
    content: str


# =========================================================
# RETRIEVAL RESULT
# =========================================================


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    policy_id: str
    title: str
    source: str
    chunk_index: int
    content: str
    distance: float


# =========================================================
# RAG RESPONSE
# =========================================================


@dataclass(frozen=True)
class RAGResponse:
    question: str
    answer: str
    retrieved_policy_ids: list[str]
    retrieval_context: list[str]
