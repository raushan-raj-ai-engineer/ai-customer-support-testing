from __future__ import annotations

from typing import Any

from app.agent.router import (
    SupportIntentRouter,
)
from app.agent.workflow import (
    SupportAgent,
)

# =========================================================
# FAKE TOOLS
# =========================================================


class FakeTools:
    """
    Deterministic fake tools.

    No Ollama.
    No Chroma.
    No real ticket side effects.
    """

    def rag(
        self,
        question: str,
    ) -> dict[str, Any]:

        text = question.lower()

        # -------------------------------------------------
        # RETURN POLICY
        # -------------------------------------------------

        if "return" in text or "refund" in text:
            return {
                "answer": (
                    "Eligible products may be "
                    "returned within 30 days "
                    "of the original purchase date."
                ),
                "retrieved_policy_ids": ["REFUND_POLICY"],
                "retrieval_context": [
                    (
                        "Customers may return eligible "
                        "products within 30 days of the "
                        "original purchase date."
                    )
                ],
            }

        # -------------------------------------------------
        # PASSWORD
        # -------------------------------------------------

        if "password" in text:
            return {
                "answer": ("The password reset link expires after 15 minutes."),
                "retrieved_policy_ids": ["PASSWORD_POLICY"],
                "retrieval_context": [
                    ("The password reset link expires after 15 minutes.")
                ],
            }

        # -------------------------------------------------
        # SHIPPING
        # -------------------------------------------------

        return {
            "answer": ("Standard shipping normally takes 3 to 5 business days."),
            "retrieved_policy_ids": ["SHIPPING_POLICY"],
            "retrieval_context": [
                ("Standard shipping normally takes 3 to 5 business days.")
            ],
        }

    def order(
        self,
        order_id: str,
    ) -> dict[str, Any] | None:

        if order_id != "ORD-1001":
            return None

        return {
            "order_id": ("ORD-1001"),
            "status": ("SHIPPED"),
            "tracking_number": ("TRK-90001"),
            "estimated_delivery": ("2026-09-05"),
        }

    def ticket(
        self,
        description: str,
        order_id: str | None = None,
    ) -> dict[str, Any]:

        return {
            "ticket_id": ("TKT-TEST-001"),
            "description": (description),
            "order_id": (order_id),
        }


# =========================================================
# BUILD AGENT
# =========================================================


def build_agent() -> SupportAgent:

    return SupportAgent(
        router=(SupportIntentRouter(use_llm=False)),
        tools=FakeTools(),  # type: ignore[arg-type]
    )


# =========================================================
# POLICY FLOW
# =========================================================


def test_policy_uses_only_rag_tool():

    result = build_agent().run("How long does standard shipping take?")

    assert result.intent == "policy"

    assert result.task_completed is True

    assert "3 to 5" in result.answer

    assert [call.name for call in result.tool_calls] == ["rag_policy_lookup"]


# =========================================================
# ORDER FLOW
# =========================================================


def test_order_uses_order_tool():

    result = build_agent().run("Where is ORD-1001?")

    assert result.intent == "order"

    assert result.task_completed is True

    assert "SHIPPED" in result.answer

    assert "ORD-1001" in result.answer

    assert [call.name for call in result.tool_calls] == ["order_lookup"]


# =========================================================
# UNKNOWN ORDER
# =========================================================


def test_unknown_order_fails_task_completion():

    result = build_agent().run("Where is ORD-9999?")

    assert result.intent == "order"

    assert result.task_completed is False

    assert result.error is not None

    assert "ORD-9999" in result.answer

    assert "not found" in result.answer.lower()

    assert [call.name for call in result.tool_calls] == ["order_lookup"]


# =========================================================
# TICKET FLOW
# =========================================================


def test_ticket_uses_ticket_tool():

    result = build_agent().run("Create a ticket because my shipment is delayed.")

    assert result.intent == "ticket"

    assert result.task_completed is True

    assert "TKT-TEST-001" in result.answer

    assert [call.name for call in result.tool_calls] == ["ticket_create"]


# =========================================================
# ORDER + POLICY FLOW
# =========================================================


def test_order_policy_uses_order_then_rag():

    result = build_agent().run("Can I return ORD-1001?")

    assert result.intent == "order_policy"

    assert result.task_completed is True

    tool_names = [call.name for call in result.tool_calls]

    assert tool_names == [
        "order_lookup",
        "rag_policy_lookup",
    ]

    assert "ORD-1001" in result.answer

    assert "30 days" in result.answer


# =========================================================
# POLICY-FOCUSED RAG QUERY
# =========================================================


def test_order_policy_uses_policy_focused_rag_query():

    captured_questions: list[str] = []

    class CapturingTools(FakeTools):
        def rag(
            self,
            question: str,
        ) -> dict[str, Any]:

            captured_questions.append(question)

            return {
                "answer": (
                    "Eligible products may be "
                    "returned within 30 days "
                    "of the original purchase date."
                ),
                "retrieved_policy_ids": ["REFUND_POLICY"],
                "retrieval_context": [
                    (
                        "Customers may return eligible "
                        "products within 30 days of the "
                        "original purchase date."
                    )
                ],
            }

    agent = SupportAgent(
        router=(SupportIntentRouter(use_llm=False)),
        tools=CapturingTools(),  # type: ignore[arg-type]
    )

    result = agent.run("Can I return ORD-1001?")

    assert result.intent == "order_policy"

    assert captured_questions == [
        (
            "What is the refund and return "
            "policy, including the return "
            "window for eligible products?"
        )
    ]

    assert "30" in result.answer


# =========================================================
# ORDER ID MUST NOT GO TO RAG
# =========================================================


def test_order_id_is_not_sent_to_policy_rag():

    captured_questions: list[str] = []

    class CapturingTools(FakeTools):
        def rag(
            self,
            question: str,
        ) -> dict[str, Any]:

            captured_questions.append(question)

            return super().rag(question)

    agent = SupportAgent(
        router=(SupportIntentRouter(use_llm=False)),
        tools=CapturingTools(),  # type: ignore[arg-type]
    )

    agent.run("Can I return ORD-1001?")

    assert len(captured_questions) == 1

    assert "ORD-1001" not in captured_questions[0]


# =========================================================
# RETURN ELIGIBILITY SAFETY
# =========================================================


def test_order_policy_does_not_invent_specific_eligibility():

    result = build_agent().run("Can I return ORD-1001?")

    assert "30 days" in result.answer

    assert "cannot confirm" in result.answer.lower()

    assert "purchase date" in result.answer.lower()

    assert "yes, ord-1001" not in result.answer.lower()


# =========================================================
# UNSUPPORTED
# =========================================================


def test_unsupported_request_calls_no_tool():

    result = build_agent().run("Tell me a joke.")

    assert result.intent == "unsupported"

    assert result.task_completed is False

    assert result.tool_calls == []


# =========================================================
# APPROVED TOOLS
# =========================================================


def test_agent_can_only_call_approved_tools():

    questions = [
        ("How long does shipping take?"),
        ("Where is ORD-1001?"),
        ("Create a ticket for my problem."),
        ("Can I return ORD-1001?"),
    ]

    allowed_tools = {
        "rag_policy_lookup",
        "order_lookup",
        "ticket_create",
    }

    agent = build_agent()

    for question in questions:
        result = agent.run(question)

        actual_tools = {call.name for call in result.tool_calls}

        assert actual_tools <= allowed_tools


# =========================================================
# TRAJECTORY
# =========================================================


def test_agent_records_order_trajectory():

    result = build_agent().run("Where is ORD-1001?")

    assert result.trajectory[0] == "router:order"

    assert "tool:order" in result.trajectory

    assert result.trajectory[-1] == "finalize"


# =========================================================
# MULTI-TOOL TRAJECTORY
# =========================================================


def test_order_policy_records_correct_trajectory():

    result = build_agent().run("Can I return ORD-1001?")

    assert result.trajectory == [
        "router:order_policy",
        "tool:order",
        "tool:rag",
        "finalize",
    ]


# =========================================================
# TOOL CALL INPUT GROUNDING
# =========================================================


def test_order_policy_tool_arguments_are_grounded():

    result = build_agent().run("Can I return ORD-1001?")

    assert len(result.tool_calls) == 2

    order_call = result.tool_calls[0]

    rag_call = result.tool_calls[1]

    assert order_call.name == "order_lookup"

    assert order_call.input["order_id"] == "ORD-1001"

    assert rag_call.name == "rag_policy_lookup"

    rag_question = str(rag_call.input["question"])

    assert "return" in rag_question.lower()

    assert "ORD-1001" not in rag_question
