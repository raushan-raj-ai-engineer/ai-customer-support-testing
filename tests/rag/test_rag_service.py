from __future__ import annotations

from typing import Any

from app.rag.rag_service import (
    RAGService,
    format_retrieval_context,
    unique_policy_ids,
)

# =========================================================
# FAKE LANGCHAIN
#
# Important:
# unit tests should not require a live LLM.
# =========================================================


class FakeRAGChain:
    def __init__(
        self,
    ) -> None:

        self.last_input: dict[str, Any] | None = None

    def invoke(
        self,
        values: dict[str, Any],
    ) -> str:

        self.last_input = values

        return "Eligible products can be returned within 30 days."


# =========================================================
# CONTEXT TEST
# =========================================================


def test_format_retrieval_context(
    policy_vector_store,
):

    hits = policy_vector_store.search(
        query=("Can I return my product?"),
        n_results=2,
    )

    context = format_retrieval_context(hits)

    assert "Policy ID:" in context

    assert "Content:" in context


# =========================================================
# UNIQUE POLICY TEST
# =========================================================


def test_unique_policy_ids(
    policy_vector_store,
):

    hits = policy_vector_store.search(
        query=("How long does shipping take?"),
        n_results=3,
    )

    result = unique_policy_ids(hits)

    assert len(result) == len(set(result))


# =========================================================
# RAG SERVICE CONTRACT TEST
# =========================================================


def test_rag_service_passes_context_to_chain(
    policy_vector_store,
):

    fake_chain = FakeRAGChain()

    service = RAGService(
        vector_store=(policy_vector_store),
        chain=fake_chain,
        top_k=3,
    )

    result = service.ask("Can I return my laptop after 20 days?")

    assert result.question == ("Can I return my laptop after 20 days?")

    assert result.answer == ("Eligible products can be returned within 30 days.")

    assert result.retrieved_policy_ids[0] == "REFUND_POLICY"

    assert result.retrieval_context

    assert fake_chain.last_input is not None

    assert "30 days" in str(fake_chain.last_input["context"])


# =========================================================
# EMPTY QUESTION
# =========================================================


def test_rag_service_rejects_empty_question(
    policy_vector_store,
):

    service = RAGService(
        vector_store=(policy_vector_store),
        chain=FakeRAGChain(),
    )

    try:
        service.ask("   ")

        assert False

    except ValueError as exc:
        assert "Question cannot be empty" in str(exc)
