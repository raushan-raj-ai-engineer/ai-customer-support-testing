from __future__ import annotations

from typing import Any, Literal

from pydantic import (
    BaseModel,
    Field,
)

# =========================================================
# AGENT INTENTS
# =========================================================


AgentIntent = Literal[
    "policy",
    "order",
    "ticket",
    "order_policy",
    "unsupported",
]


# =========================================================
# ROUTER DECISION
# =========================================================


class IntentDecision(BaseModel):
    intent: AgentIntent

    order_id: str | None = None

    ticket_description: str | None = None

    reason: str = Field(min_length=1)


# =========================================================
# TOOL CALL RECORD
# =========================================================


class ToolCallRecord(BaseModel):
    name: str

    input: dict[
        str,
        Any,
    ]

    success: bool

    output: Any | None = None

    error: str | None = None


# =========================================================
# API REQUEST
# =========================================================


class AgentChatRequest(BaseModel):
    message: str = Field(
        min_length=2,
        max_length=2000,
    )


# =========================================================
# API RESPONSE
# =========================================================


class AgentChatResponse(BaseModel):
    message: str

    intent: AgentIntent

    answer: str

    tool_calls: list[ToolCallRecord]

    trajectory: list[str]

    task_completed: bool

    error: str | None = None
