from __future__ import annotations

from functools import (
    lru_cache,
)
from typing import (
    Any,
)

from langsmith import (
    traceable,
)

from app.agent.tools import (
    SupportTools,
)
from app.agent.workflow import (
    SupportAgent,
)

# =========================================================
# OBSERVABLE TOOLS
# =========================================================


class ObservableSupportTools(SupportTools):
    """
    SupportTools with explicit LangSmith
    tool-level tracing.

    LangGraph nodes are already traced when
    LangSmith tracing is enabled.

    These decorators give us an additional
    clear tool-level child trace.
    """

    @traceable(
        run_type="tool",
        name="RAG Policy Tool",
        tags=[
            "rag",
            "policy",
            "support-tool",
        ],
    )
    def rag(
        self,
        question: str,
    ) -> dict[str, Any]:

        return super().rag(question)

    @traceable(
        run_type="tool",
        name="Order Lookup Tool",
        tags=[
            "order",
            "support-tool",
        ],
    )
    def order(
        self,
        order_id: str,
    ) -> (
        dict[
            str,
            Any,
        ]
        | None
    ):

        return super().order(order_id)

    @traceable(
        run_type="tool",
        name="Ticket Creation Tool",
        tags=[
            "ticket",
            "support-tool",
        ],
    )
    def ticket(
        self,
        description: str,
        order_id: str | None = None,
    ) -> dict[str, Any]:

        return super().ticket(
            description=description,
            order_id=order_id,
        )


# =========================================================
# OBSERVABLE AGENT
# =========================================================


@lru_cache(maxsize=1)
def get_observable_agent() -> SupportAgent:

    tools = ObservableSupportTools()

    return SupportAgent(tools=tools)


# =========================================================
# TOP LEVEL TRACE
# =========================================================


@traceable(
    run_type="chain",
    name="Customer Support Agent Request",
    tags=[
        "stage6",
        "langgraph",
        "customer-support",
        "agent",
    ],
    metadata={
        "application": ("ai-customer-support-testing"),
        "stage": 6,
        "generator_model": ("ollama:llama3.2"),
    },
)
def run_traced_agent(
    message: str,
) -> dict[str, Any]:
    """
    Execute the production support agent
    inside a top-level LangSmith trace.

    Expected trace hierarchy:

        Customer Support Agent Request
            ↓
        LangGraph
            ↓
        Router
            ↓
        Tool node
            ↓
        Explicit tool trace
            ↓
        LangChain/Ollama
    """

    message = message.strip()

    if not message:
        raise ValueError("Message cannot be empty")

    agent = get_observable_agent()

    result = agent.run(message)

    return result.model_dump()
