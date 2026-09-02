from __future__ import annotations

import re
from typing import Any

from app.agent.models import (
    AgentIntent,
)
from app.agent.tools import (
    SupportTools,
)
from app.security.input_guard import (
    InputGuard,
)

# =========================================================
# ERROR
# =========================================================


class ToolAuthorizationError(PermissionError):
    pass


# =========================================================
# ORDER ID VALIDATION
# =========================================================


ORDER_ID_PATTERN = re.compile(
    r"^ORD-\d{4,10}$",
    re.IGNORECASE,
)


# =========================================================
# POLICY
# =========================================================


class ToolPolicy:
    """
    Deterministic least-privilege policy.

    Each intent has an exact maximum tool sequence.
    """

    TOOL_SEQUENCE: dict[
        AgentIntent,
        list[str],
    ] = {
        "policy": ["rag_policy_lookup"],
        "order": ["order_lookup"],
        "ticket": ["ticket_create"],
        "order_policy": [
            "order_lookup",
            "rag_policy_lookup",
        ],
        "unsupported": [],
    }

    WRITE_TOOLS = {"ticket_create"}

    def expected_sequence(
        self,
        intent: AgentIntent,
    ) -> list[str]:

        return list(self.TOOL_SEQUENCE[intent])

    # =====================================================
    # TOOL AUTHORIZATION
    # =====================================================

    def authorize(
        self,
        *,
        intent: AgentIntent,
        tool_name: str,
        arguments: dict[
            str,
            Any,
        ],
        executed_tools: list[str],
        approve_write: bool,
    ) -> None:

        expected = self.expected_sequence(intent)

        next_index = len(executed_tools)

        # -------------------------------------------------
        # EXTRA / UNKNOWN TOOL
        # -------------------------------------------------

        if next_index >= len(expected):
            raise ToolAuthorizationError(
                f"No additional tool call is authorized for intent '{intent}'."
            )

        expected_tool = expected[next_index]

        # -------------------------------------------------
        # SEQUENCE
        # -------------------------------------------------

        if tool_name != expected_tool:
            raise ToolAuthorizationError(
                f"Tool '{tool_name}' is not "
                "authorized at this point. "
                f"Expected '{expected_tool}'."
            )

        # -------------------------------------------------
        # WRITE APPROVAL
        # -------------------------------------------------

        if tool_name in self.WRITE_TOOLS and not approve_write:
            raise ToolAuthorizationError(
                "Write operation requires explicit customer approval."
            )

        # -------------------------------------------------
        # TOOL ARGUMENT VALIDATION
        # -------------------------------------------------

        self.validate_arguments(
            tool_name=tool_name,
            arguments=arguments,
        )

    # =====================================================
    # ARGUMENT VALIDATION
    # =====================================================

    def validate_arguments(
        self,
        *,
        tool_name: str,
        arguments: dict[
            str,
            Any,
        ],
    ) -> None:

        if tool_name == "order_lookup":
            order_id = arguments.get("order_id")

            if not isinstance(
                order_id,
                str,
            ):
                raise ToolAuthorizationError("order_lookup requires a string order_id.")

            if ORDER_ID_PATTERN.fullmatch(order_id) is None:
                raise ToolAuthorizationError("Invalid order ID format.")

            return

        # -------------------------------------------------
        # RAG
        # -------------------------------------------------

        if tool_name == "rag_policy_lookup":
            question = arguments.get("question")

            if not isinstance(
                question,
                str,
            ):
                raise ToolAuthorizationError("RAG tool requires a string question.")

            question = question.strip()

            if not question:
                raise ToolAuthorizationError("RAG question cannot be empty.")

            if len(question) > 1000:
                raise ToolAuthorizationError("RAG question exceeds allowed length.")

            # Defense in depth:
            # internally-generated tool inputs
            # are checked again.

            guard_result = InputGuard().inspect(question)

            if not (guard_result.allowed):
                raise ToolAuthorizationError("Unsafe RAG tool input was blocked.")

            return

        # -------------------------------------------------
        # TICKET
        # -------------------------------------------------

        if tool_name == "ticket_create":
            description = arguments.get("description")

            if not isinstance(
                description,
                str,
            ):
                raise ToolAuthorizationError(
                    "ticket_create requires a string description."
                )

            if not (description.strip()):
                raise ToolAuthorizationError("Ticket description cannot be empty.")

            if len(description) > 1000:
                raise ToolAuthorizationError(
                    "Ticket description exceeds allowed length."
                )

            order_id = arguments.get("order_id")

            if order_id is not None:
                if not isinstance(
                    order_id,
                    str,
                ):
                    raise ToolAuthorizationError("Ticket order_id must be a string.")

                if ORDER_ID_PATTERN.fullmatch(order_id) is None:
                    raise ToolAuthorizationError("Invalid ticket order ID format.")

            return

        # -------------------------------------------------
        # UNKNOWN
        # -------------------------------------------------

        raise ToolAuthorizationError(f"Unknown tool '{tool_name}'.")


# =========================================================
# GUARDED TOOL WRAPPER
# =========================================================


class GuardedSupportTools(SupportTools):
    """
    Wrap real SupportTools.

    Authorization happens BEFORE the underlying
    tool executes.
    """

    def __init__(
        self,
        *,
        base_tools: SupportTools,
        intent: AgentIntent,
        approve_write: bool,
        policy: ToolPolicy | None = None,
    ) -> None:

        # Intentionally do not call SupportTools.__init__.
        # We delegate to the already-configured base tools.

        self.base_tools = base_tools

        self.intent: AgentIntent = intent

        self.approve_write = approve_write

        self.policy = policy or ToolPolicy()

        self.executed_tools: list[str] = []

    # =====================================================
    # AUTHORIZE
    # =====================================================

    def _authorize(
        self,
        tool_name: str,
        arguments: dict[
            str,
            Any,
        ],
    ) -> None:

        self.policy.authorize(
            intent=self.intent,
            tool_name=tool_name,
            arguments=arguments,
            executed_tools=(self.executed_tools),
            approve_write=(self.approve_write),
        )

        # Record after authorization and before execution.
        # This also prevents retry loops from silently
        # invoking the same tool repeatedly.

        self.executed_tools.append(tool_name)

    # =====================================================
    # RAG
    # =====================================================

    def rag(
        self,
        question: str,
    ) -> dict[str, Any]:

        arguments = {"question": question}

        self._authorize(
            "rag_policy_lookup",
            arguments,
        )

        return self.base_tools.rag(question)

    # =====================================================
    # ORDER
    # =====================================================

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

        arguments = {"order_id": order_id}

        self._authorize(
            "order_lookup",
            arguments,
        )

        return self.base_tools.order(order_id)

    # =====================================================
    # TICKET
    # =====================================================

    def ticket(
        self,
        description: str,
        order_id: str | None = None,
    ) -> dict[str, Any]:

        arguments = {
            "description": (description),
            "order_id": (order_id),
        }

        self._authorize(
            "ticket_create",
            arguments,
        )

        return self.base_tools.ticket(
            description=description,
            order_id=order_id,
        )
