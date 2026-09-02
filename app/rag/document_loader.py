from __future__ import annotations

from app.data import POLICIES
from app.knowledge import KNOWLEDGE_BASE
from app.rag.models import KnowledgeDocument


def load_knowledge_documents() -> list[KnowledgeDocument]:

    documents: list[KnowledgeDocument] = []

    for config in POLICIES.values():
        file_path = KNOWLEDGE_BASE / config["filename"]

        if not file_path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")

        documents.append(
            KnowledgeDocument(
                policy_id=config["policy_id"],
                title=config["title"],
                source=config["filename"],
                content=content,
            )
        )

    return documents
