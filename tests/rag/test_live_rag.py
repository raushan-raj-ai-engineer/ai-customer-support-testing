from __future__ import annotations

import os

import pytest

from app.rag.rag_service import (
    RAGService,
)

pytestmark = [
    pytest.mark.live_llm,
]


RUN_LIVE = (
    os.getenv(
        "RUN_LIVE_LLM",
        "0",
    )
    == "1"
)


@pytest.fixture(scope="module")
def live_rag_service():

    return RAGService()


# =========================================================
# REFUND
# =========================================================


@pytest.mark.skipif(
    not RUN_LIVE,
    reason=("Set RUN_LIVE_LLM=1 to run Ollama tests"),
)
def test_live_refund_answer(
    live_rag_service,
):

    response = live_rag_service.ask("Can I return my laptop after 20 days?")

    print()
    print(response.answer)

    assert response.retrieved_policy_ids[0] == "REFUND_POLICY"

    assert "30" in response.answer


# =========================================================
# SHIPPING
# =========================================================


@pytest.mark.skipif(
    not RUN_LIVE,
    reason=("Set RUN_LIVE_LLM=1 to run Ollama tests"),
)
def test_live_shipping_answer(
    live_rag_service,
):

    response = live_rag_service.ask("How long does normal shipping take?")

    print()
    print(response.answer)

    assert response.retrieved_policy_ids[0] == "SHIPPING_POLICY"

    assert "3" in response.answer

    assert "5" in response.answer


# =========================================================
# PASSWORD
# =========================================================


@pytest.mark.skipif(
    not RUN_LIVE,
    reason=("Set RUN_LIVE_LLM=1 to run Ollama tests"),
)
def test_live_password_answer(
    live_rag_service,
):

    response = live_rag_service.ask("How long does a password reset link remain valid?")

    print()
    print(response.answer)

    assert response.retrieved_policy_ids[0] == "PASSWORD_POLICY"

    assert "15" in response.answer
