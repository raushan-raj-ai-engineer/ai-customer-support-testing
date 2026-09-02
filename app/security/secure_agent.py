from __future__ import annotations

from app.agent.models import (
    IntentDecision,
)
from app.agent.router import (
    SupportIntentRouter,
)
from app.agent.tools import (
    SupportTools,
)
from app.agent.workflow import (
    SupportAgent,
)
from app.security.input_guard import (
    InputGuard,
)
from app.security.models import (
    SecureAgentChatResponse,
    SecurityFinding,
)
from app.security.output_guard import (
    OutputGuard,
)
from app.security.tool_policy import (
    GuardedSupportTools,
    ToolPolicy,
)

# =========================================================
# FIXED ROUTER
# =========================================================


class FixedIntentRouter(SupportIntentRouter):
    """
    The security layer performs routing exactly once.

    LangGraph then receives the already-approved
    routing decision.

    This avoids a second LLM routing decision that
    might change intent after authorization.
    """

    def __init__(
        self,
        decision: IntentDecision,
    ) -> None:

        super().__init__(use_llm=False)

        self.decision = decision

    def route(
        self,
        message: str,
    ) -> IntentDecision:

        return self.decision.model_copy(deep=True)


# =========================================================
# SECURE AGENT
# =========================================================


class SecureSupportAgent:
    def __init__(
        self,
        router: SupportIntentRouter | None = None,
        base_tools: SupportTools | None = None,
        input_guard: InputGuard | None = None,
        output_guard: OutputGuard | None = None,
        tool_policy: ToolPolicy | None = None,
    ) -> None:

        self.router = router or SupportIntentRouter()

        self.base_tools = base_tools or SupportTools()

        self.input_guard = input_guard or InputGuard()

        self.output_guard = output_guard or OutputGuard()

        self.tool_policy = tool_policy or ToolPolicy()

    # =====================================================
    # BLOCKED RESPONSE
    # =====================================================

    @staticmethod
    def _blocked_response(
        *,
        message: str,
        findings: list[SecurityFinding],
        answer: str,
        trajectory_event: str,
    ) -> SecureAgentChatResponse:

        return SecureAgentChatResponse(
            message=message,
            intent="unsupported",
            answer=answer,
            tool_calls=[],
            trajectory=[trajectory_event],
            task_completed=False,
            blocked=True,
            security_findings=(findings),
            error=None,
        )

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
        message: str,
        *,
        approve_write: bool = False,
    ) -> SecureAgentChatResponse:

        # =================================================
        # STEP 1
        # INPUT SECURITY
        # =================================================

        input_result = self.input_guard.inspect(message)

        if not (input_result.allowed):
            return self._blocked_response(
                message=("[BLOCKED_INPUT]"),
                findings=(input_result.findings),
                answer=(
                    "I can't process that request "
                    "because it violates the "
                    "support agent's security policy."
                ),
                trajectory_event=("security:input_blocked"),
            )

        sanitized_message = input_result.sanitized_input

        # =================================================
        # STEP 2
        # ROUTING
        # =================================================

        decision = self.router.route(sanitized_message)

        # =================================================
        # STEP 3
        # HUMAN APPROVAL FOR WRITE ACTION
        # =================================================

        if decision.intent == "ticket" and not approve_write:
            finding = SecurityFinding(
                rule_id=("SEC-WRITE-001"),
                category=("write_approval"),
                severity="medium",
                message=(
                    "Ticket creation requires "
                    "explicit approval before "
                    "the write tool executes."
                ),
            )

            return SecureAgentChatResponse(
                message=(sanitized_message),
                intent=(decision.intent),
                answer=(
                    "I can create the support ticket, "
                    "but the write action requires "
                    "explicit approval."
                ),
                tool_calls=[],
                trajectory=[
                    (f"router:{decision.intent}"),
                    ("security:write_approval_required"),
                ],
                task_completed=False,
                blocked=True,
                security_findings=[
                    *input_result.findings,
                    finding,
                ],
                error=None,
            )

        # =================================================
        # STEP 4
        # BUILD AUTHORIZED TOOL BOUNDARY
        # =================================================

        guarded_tools = GuardedSupportTools(
            base_tools=(self.base_tools),
            intent=(decision.intent),
            approve_write=(approve_write),
            policy=(self.tool_policy),
        )

        # =================================================
        # STEP 5
        # LOCK ROUTE
        # =================================================

        fixed_router = FixedIntentRouter(decision)

        # =================================================
        # STEP 6
        # EXECUTE LANGGRAPH
        # =================================================

        agent = SupportAgent(
            router=(fixed_router),
            tools=(guarded_tools),
        )

        result = agent.run(sanitized_message)

        # =================================================
        # STEP 7
        # TOOL HISTORY DEFENSE-IN-DEPTH
        # =================================================

        actual_tools = [call.name for call in result.tool_calls]

        expected_tools = self.tool_policy.expected_sequence(decision.intent)

        # Actual may be a prefix when execution fails,
        # e.g. unknown order in order_policy flow.

        allowed_prefix = expected_tools[: len(actual_tools)]

        if actual_tools != allowed_prefix:
            finding = SecurityFinding(
                rule_id=("SEC-TOOL-002"),
                category=("tool_authorization"),
                severity="critical",
                message=(
                    "Observed tool trajectory violated the authorized tool sequence."
                ),
            )

            return SecureAgentChatResponse(
                message=(sanitized_message),
                intent=(decision.intent),
                answer=(
                    "The request was stopped "
                    "because an unauthorized "
                    "tool trajectory was detected."
                ),
                tool_calls=(result.tool_calls),
                trajectory=[
                    *result.trajectory,
                    ("security:tool_sequence_blocked"),
                ],
                task_completed=False,
                blocked=True,
                security_findings=[
                    *input_result.findings,
                    finding,
                ],
                error=("Unauthorized tool sequence."),
            )

        # =================================================
        # STEP 8
        # OUTPUT SECURITY
        # =================================================

        output_result = self.output_guard.inspect(result.answer)

        all_findings = [
            *input_result.findings,
            *output_result.findings,
        ]

        if not (output_result.allowed):
            return SecureAgentChatResponse(
                message=(sanitized_message),
                intent=(decision.intent),
                answer=(output_result.sanitized_output),
                tool_calls=(result.tool_calls),
                trajectory=[
                    *result.trajectory,
                    ("security:output_blocked"),
                ],
                task_completed=False,
                blocked=True,
                security_findings=(all_findings),
                error=None,
            )

        # =================================================
        # SUCCESS
        # =================================================

        return SecureAgentChatResponse(
            message=(sanitized_message),
            intent=(decision.intent),
            answer=(output_result.sanitized_output),
            tool_calls=(result.tool_calls),
            trajectory=(result.trajectory),
            task_completed=(result.task_completed),
            blocked=False,
            security_findings=(all_findings),
            error=(result.error),
        )
