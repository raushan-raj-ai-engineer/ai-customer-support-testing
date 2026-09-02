from __future__ import annotations

from typing import (
    Any,
    NotRequired,
    Required,
    TypedDict,
)

from app.agent.models import (
    AgentIntent,
    ToolCallRecord,
)


class SupportAgentState(
    TypedDict,
    total=False,
):
    """
    Shared LangGraph state.

    Required fields:
        These fields are guaranteed when the graph starts.

    Optional fields:
        These fields are populated progressively
        by different graph nodes.
    """

    # =====================================================
    # REQUIRED INPUT STATE
    # =====================================================

    user_input: Required[str]

    tool_calls: Required[list[ToolCallRecord]]

    trajectory: Required[list[str]]

    # =====================================================
    # ROUTER OUTPUT
    # =====================================================

    intent: NotRequired[AgentIntent]

    order_id: NotRequired[str | None]

    ticket_description: NotRequired[str | None]

    route_reason: NotRequired[str]

    # =====================================================
    # RAG TOOL OUTPUT
    # =====================================================

    rag_answer: NotRequired[str]

    retrieved_policy_ids: NotRequired[list[str]]

    retrieval_context: NotRequired[list[str]]

    # =====================================================
    # ORDER TOOL OUTPUT
    # =====================================================

    order_data: NotRequired[dict[str, Any] | None]

    # =====================================================
    # TICKET TOOL OUTPUT
    # =====================================================

    ticket_data: NotRequired[dict[str, Any] | None]

    # =====================================================
    # FINAL OUTPUT
    # =====================================================

    final_answer: NotRequired[str]

    task_completed: NotRequired[bool]

    error: NotRequired[str | None]
