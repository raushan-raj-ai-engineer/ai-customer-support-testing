from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)

from app.agent.models import (
    AgentIntent,
    ToolCallRecord,
)

# =========================================================
# SECURITY TYPES
# =========================================================


SecuritySeverity = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


SecurityCategory = Literal[
    "prompt_injection",
    "prompt_leakage",
    "tool_manipulation",
    "secret_exfiltration",
    "sensitive_data",
    "tool_authorization",
    "output_leakage",
    "input_limits",
    "write_approval",
]


# =========================================================
# SECURITY FINDING
# =========================================================


class SecurityFinding(BaseModel):
    rule_id: str = Field(min_length=1)

    category: SecurityCategory

    severity: SecuritySeverity

    message: str = Field(min_length=1)


# =========================================================
# INPUT GUARD RESULT
# =========================================================


class InputGuardResult(BaseModel):
    allowed: bool

    sanitized_input: str

    findings: list[SecurityFinding] = Field(default_factory=list)


# =========================================================
# OUTPUT GUARD RESULT
# =========================================================


class OutputGuardResult(BaseModel):
    allowed: bool

    sanitized_output: str

    findings: list[SecurityFinding] = Field(default_factory=list)


# =========================================================
# SECURE API REQUEST
# =========================================================


class SecureAgentChatRequest(BaseModel):
    message: str = Field(
        min_length=2,
        max_length=2000,
    )

    approve_write: bool = False


# =========================================================
# SECURE RESPONSE
# =========================================================


class SecureAgentChatResponse(BaseModel):
    # Important:
    # This is sanitized text, not necessarily
    # the customer's raw sensitive input.

    message: str

    intent: AgentIntent

    answer: str

    tool_calls: list[ToolCallRecord]

    trajectory: list[str]

    task_completed: bool

    blocked: bool

    security_findings: list[SecurityFinding]

    error: str | None = None
