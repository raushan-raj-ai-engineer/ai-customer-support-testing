from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agent.models import (
    AgentChatResponse,
    ToolCallRecord,
)
from app.agent.router import (
    SupportIntentRouter,
)
from app.agent.state import (
    SupportAgentState,
)
from app.agent.tools import (
    SupportTools,
)

# =========================================================
# GRAPH ROUTES
# =========================================================


RouteTarget = Literal[
    "rag_tool",
    "order_tool",
    "ticket_tool",
    "finalize",
]


# =========================================================
# CONSTANTS
# =========================================================


RAG_FALLBACK_ANSWER = "I don't know based on the available support policies."


# =========================================================
# TRAJECTORY HELPER
# =========================================================


def _trajectory(
    state: SupportAgentState,
    event: str,
) -> list[str]:
    """
    Return existing trajectory plus one new event.
    """

    existing = list(
        state.get(
            "trajectory",
            [],
        )
    )

    existing.append(event)

    return existing


# =========================================================
# TOOL CALL HISTORY HELPER
# =========================================================


def _tool_calls(
    state: SupportAgentState,
    call: ToolCallRecord,
) -> list[ToolCallRecord]:
    """
    Return existing tool-call history plus
    the latest tool call.
    """

    existing = list(
        state.get(
            "tool_calls",
            [],
        )
    )

    existing.append(call)

    return existing


# =========================================================
# DISPLAY VALUE
# =========================================================


def _display_value(
    value: Any,
) -> str:
    """
    Convert Enum values into customer-friendly text.

    Example:

        OrderStatus.SHIPPED
            ↓
        SHIPPED
    """

    if isinstance(
        value,
        Enum,
    ):
        return str(value.value)

    return str(value)


# =========================================================
# POLICY QUERY DECOMPOSITION
# =========================================================


def _build_policy_question(
    state: SupportAgentState,
) -> str:
    """
    Convert a multi-domain order+policy request into
    a policy-focused RAG query.

    Why?

    Customer:
        Can I return ORD-1001?

    Order Tool needs:
        ORD-1001

    RAG needs:
        return policy / return window

    Passing ORD-1001 directly to policy RAG can reduce
    retrieval quality because order IDs are not part
    of the support-policy knowledge base.
    """

    user_input = state["user_input"].strip()

    intent = state.get("intent")

    # -----------------------------------------------------
    # NORMAL POLICY QUESTION
    # -----------------------------------------------------

    if intent != "order_policy":
        return user_input

    text = user_input.lower()

    # -----------------------------------------------------
    # RETURN / REFUND
    # -----------------------------------------------------

    if "return" in text or "refund" in text:
        return (
            "What is the refund and return policy, "
            "including the return window for "
            "eligible products?"
        )

    # -----------------------------------------------------
    # SHIPPING / DELIVERY
    # -----------------------------------------------------

    if "shipping" in text or "delivery" in text:
        return "What is the shipping and delivery policy?"

    # -----------------------------------------------------
    # TRACKING
    # -----------------------------------------------------

    if "tracking" in text or "track" in text:
        return "What is the policy for receiving an order tracking number?"

    # -----------------------------------------------------
    # PASSWORD
    # -----------------------------------------------------

    if "password" in text or "reset" in text:
        return "What is the password reset policy?"

    # -----------------------------------------------------
    # SAFE FALLBACK
    # -----------------------------------------------------

    return user_input


# =========================================================
# SUPPORT AGENT
# =========================================================


class SupportAgent:
    """
    LangGraph customer-support agent.

    Supported flows:

        policy
            router
            → RAG
            → finalize

        order
            router
            → order lookup
            → finalize

        ticket
            router
            → ticket creation
            → finalize

        order_policy
            router
            → order lookup
            → focused policy RAG
            → finalize
    """

    def __init__(
        self,
        router: SupportIntentRouter | None = None,
        tools: SupportTools | None = None,
    ) -> None:

        self.router = router or SupportIntentRouter()

        self.tools = tools or SupportTools()

        self.graph = self._build_graph()

    # =====================================================
    # ROUTER NODE
    # =====================================================

    def _route_node(
        self,
        state: SupportAgentState,
    ) -> dict[str, Any]:

        decision = self.router.route(state["user_input"])

        return {
            "intent": (decision.intent),
            "order_id": (decision.order_id),
            "ticket_description": (decision.ticket_description),
            "route_reason": (decision.reason),
            "trajectory": (
                _trajectory(
                    state,
                    (f"router:{decision.intent}"),
                )
            ),
        }

    # =====================================================
    # ROUTE AFTER CLASSIFICATION
    # =====================================================

    def _after_route(
        self,
        state: SupportAgentState,
    ) -> RouteTarget:

        intent = state.get("intent")

        if intent == "policy":
            return "rag_tool"

        if intent in {
            "order",
            "order_policy",
        }:
            return "order_tool"

        if intent == "ticket":
            return "ticket_tool"

        return "finalize"

    # =====================================================
    # RAG TOOL NODE
    # =====================================================

    def _rag_node(
        self,
        state: SupportAgentState,
    ) -> dict[str, Any]:

        # IMPORTANT:
        #
        # For normal policy intent:
        #     original customer question
        #
        # For order_policy:
        #     policy-focused transformed question
        #
        question = _build_policy_question(state)

        try:
            result = self.tools.rag(question)

            retrieved_policy_ids = result.get(
                "retrieved_policy_ids",
                [],
            )

            retrieval_context = result.get(
                "retrieval_context",
                [],
            )

            answer = str(
                result.get(
                    "answer",
                    "",
                )
            ).strip()

            call = ToolCallRecord(
                name=("rag_policy_lookup"),
                input={"question": (question)},
                success=True,
                output={"retrieved_policy_ids": (retrieved_policy_ids)},
                error=None,
            )

            return {
                "rag_answer": (answer),
                "retrieved_policy_ids": (retrieved_policy_ids),
                "retrieval_context": (retrieval_context),
                "tool_calls": (
                    _tool_calls(
                        state,
                        call,
                    )
                ),
                "trajectory": (
                    _trajectory(
                        state,
                        "tool:rag",
                    )
                ),
            }

        except Exception as exc:
            error_message = str(exc)

            call = ToolCallRecord(
                name=("rag_policy_lookup"),
                input={"question": (question)},
                success=False,
                output=None,
                error=(error_message),
            )

            return {
                "error": (error_message),
                "tool_calls": (
                    _tool_calls(
                        state,
                        call,
                    )
                ),
                "trajectory": (
                    _trajectory(
                        state,
                        "tool:rag:failed",
                    )
                ),
            }

    # =====================================================
    # ORDER TOOL NODE
    # =====================================================

    def _order_node(
        self,
        state: SupportAgentState,
    ) -> dict[str, Any]:

        order_id = state.get("order_id")

        # -------------------------------------------------
        # ORDER ID MISSING
        # -------------------------------------------------

        if not order_id:
            message = "Order ID is required for order lookup."

            call = ToolCallRecord(
                name=("order_lookup"),
                input={},
                success=False,
                output=None,
                error=(message),
            )

            return {
                "error": (message),
                "tool_calls": (
                    _tool_calls(
                        state,
                        call,
                    )
                ),
                "trajectory": (
                    _trajectory(
                        state,
                        "tool:order:failed",
                    )
                ),
            }

        # -------------------------------------------------
        # ORDER LOOKUP
        # -------------------------------------------------

        try:
            order = self.tools.order(order_id)

            # ---------------------------------------------
            # NOT FOUND
            # ---------------------------------------------

            if order is None:
                message = f"Order '{order_id}' was not found."

                call = ToolCallRecord(
                    name=("order_lookup"),
                    input={"order_id": (order_id)},
                    success=False,
                    output=None,
                    error=(message),
                )

                return {
                    "error": (message),
                    "tool_calls": (
                        _tool_calls(
                            state,
                            call,
                        )
                    ),
                    "trajectory": (
                        _trajectory(
                            state,
                            ("tool:order:not_found"),
                        )
                    ),
                }

            # ---------------------------------------------
            # SUCCESS
            # ---------------------------------------------

            call = ToolCallRecord(
                name=("order_lookup"),
                input={"order_id": (order_id)},
                success=True,
                output=(order),
                error=None,
            )

            return {
                "order_data": (order),
                "tool_calls": (
                    _tool_calls(
                        state,
                        call,
                    )
                ),
                "trajectory": (
                    _trajectory(
                        state,
                        "tool:order",
                    )
                ),
            }

        except Exception as exc:
            error_message = str(exc)

            call = ToolCallRecord(
                name=("order_lookup"),
                input={"order_id": (order_id)},
                success=False,
                output=None,
                error=(error_message),
            )

            return {
                "error": (error_message),
                "tool_calls": (
                    _tool_calls(
                        state,
                        call,
                    )
                ),
                "trajectory": (
                    _trajectory(
                        state,
                        "tool:order:failed",
                    )
                ),
            }

    # =====================================================
    # AFTER ORDER
    # =====================================================

    def _after_order(
        self,
        state: SupportAgentState,
    ) -> RouteTarget:

        # -------------------------------------------------
        # FAILURE
        # -------------------------------------------------

        if state.get("error"):
            return "finalize"

        # -------------------------------------------------
        # MULTI-TOOL ORDER + POLICY FLOW
        # -------------------------------------------------

        if state.get("intent") == "order_policy":
            return "rag_tool"

        # -------------------------------------------------
        # NORMAL ORDER FLOW
        # -------------------------------------------------

        return "finalize"

    # =====================================================
    # TICKET TOOL NODE
    # =====================================================

    def _ticket_node(
        self,
        state: SupportAgentState,
    ) -> dict[str, Any]:

        description = state.get("ticket_description") or state["user_input"]

        order_id = state.get("order_id")

        try:
            ticket = self.tools.ticket(
                description=(description),
                order_id=(order_id),
            )

            call = ToolCallRecord(
                name=("ticket_create"),
                input={
                    "description": (description),
                    "order_id": (order_id),
                },
                success=True,
                output=(ticket),
                error=None,
            )

            return {
                "ticket_data": (ticket),
                "tool_calls": (
                    _tool_calls(
                        state,
                        call,
                    )
                ),
                "trajectory": (
                    _trajectory(
                        state,
                        "tool:ticket",
                    )
                ),
            }

        except Exception as exc:
            error_message = str(exc)

            call = ToolCallRecord(
                name=("ticket_create"),
                input={
                    "description": (description),
                    "order_id": (order_id),
                },
                success=False,
                output=None,
                error=(error_message),
            )

            return {
                "error": (error_message),
                "tool_calls": (
                    _tool_calls(
                        state,
                        call,
                    )
                ),
                "trajectory": (
                    _trajectory(
                        state,
                        "tool:ticket:failed",
                    )
                ),
            }

    # =====================================================
    # ORDER ANSWER
    # =====================================================

    @staticmethod
    def _order_answer(
        state: SupportAgentState,
    ) -> str:

        order = state.get("order_data") or {}

        order_id = order.get("order_id") or state.get("order_id") or "unknown"

        status = order.get("status")

        tracking = order.get("tracking_number") or order.get("tracking")

        estimated = order.get("estimated_delivery")

        # -------------------------------------------------
        # BASE ANSWER
        # -------------------------------------------------

        answer = f"Order {order_id}"

        if status is not None:
            status_text = _display_value(status)

            answer += f" — status is {status_text}"

        answer += "."

        # -------------------------------------------------
        # TRACKING
        # -------------------------------------------------

        if tracking:
            answer += f" Tracking number: {_display_value(tracking)}."

        # -------------------------------------------------
        # ESTIMATED DELIVERY
        # -------------------------------------------------

        if estimated:
            answer += f" Estimated delivery: {_display_value(estimated)}."

        return answer

    # =====================================================
    # TICKET ANSWER
    # =====================================================

    @staticmethod
    def _ticket_answer(
        state: SupportAgentState,
    ) -> str:

        ticket = state.get("ticket_data") or {}

        ticket_id = ticket.get("ticket_id") or ticket.get("id")

        if ticket_id:
            return (
                f"Support ticket {_display_value(ticket_id)} was created successfully."
            )

        return "Your support ticket was created successfully."

    # =====================================================
    # ORDER + POLICY ANSWER
    # =====================================================

    def _order_policy_answer(
        self,
        state: SupportAgentState,
    ) -> str:
        """
        Combine deterministic order evidence with
        grounded policy evidence.

        Important:

        We do NOT claim a specific order is eligible
        for return when purchase-date evidence is absent.
        """

        order_answer = self._order_answer(state)

        policy_answer = state.get(
            "rag_answer",
            "",
        ).strip()

        if not policy_answer:
            return order_answer

        answer = (f"{order_answer} {policy_answer}").strip()

        # -------------------------------------------------
        # RETURN / REFUND SAFETY
        # -------------------------------------------------

        user_input = state["user_input"].lower()

        if "return" in user_input or "refund" in user_input:
            order = state.get("order_data") or {}

            purchase_date = (
                order.get("purchase_date")
                or order.get("order_date")
                or order.get("purchased_at")
            )

            if not purchase_date:
                answer += (
                    " The available order information "
                    "does not include the original "
                    "purchase date, so I cannot confirm "
                    "whether this specific order is "
                    "currently within that return window."
                )

        return answer

    # =====================================================
    # FINALIZE NODE
    # =====================================================

    def _finalize_node(
        self,
        state: SupportAgentState,
    ) -> dict[str, Any]:

        intent = state.get(
            "intent",
            "unsupported",
        )

        error = state.get("error")

        # -------------------------------------------------
        # ERROR
        # -------------------------------------------------

        if error:
            answer = f"I could not complete the request. {error}"

            completed = False

        # -------------------------------------------------
        # POLICY
        # -------------------------------------------------

        elif intent == "policy":
            policy_answer = state.get(
                "rag_answer",
                "",
            ).strip()

            answer = policy_answer or ("I could not find a policy answer.")

            completed = bool(policy_answer and (policy_answer != RAG_FALLBACK_ANSWER))

        # -------------------------------------------------
        # ORDER
        # -------------------------------------------------

        elif intent == "order":
            answer = self._order_answer(state)

            completed = bool(state.get("order_data"))

        # -------------------------------------------------
        # TICKET
        # -------------------------------------------------

        elif intent == "ticket":
            answer = self._ticket_answer(state)

            completed = bool(state.get("ticket_data"))

        # -------------------------------------------------
        # ORDER + POLICY
        # -------------------------------------------------

        elif intent == "order_policy":
            policy_answer = state.get(
                "rag_answer",
                "",
            ).strip()

            answer = self._order_policy_answer(state)

            completed = bool(
                state.get("order_data")
                and policy_answer
                and (policy_answer != RAG_FALLBACK_ANSWER)
            )

        # -------------------------------------------------
        # UNSUPPORTED
        # -------------------------------------------------

        else:
            answer = (
                "I can help with support policies, "
                "order status, and creating "
                "support tickets."
            )

            completed = False

        return {
            "final_answer": (answer),
            "task_completed": (completed),
            "trajectory": (
                _trajectory(
                    state,
                    "finalize",
                )
            ),
        }

    # =====================================================
    # BUILD GRAPH
    # =====================================================

    def _build_graph(
        self,
    ):
        """
        Build and compile LangGraph workflow.
        """

        graph = StateGraph(SupportAgentState)

        # -------------------------------------------------
        # NODES
        # -------------------------------------------------

        graph.add_node(
            "route",
            self._route_node,
        )

        graph.add_node(
            "rag_tool",
            self._rag_node,
        )

        graph.add_node(
            "order_tool",
            self._order_node,
        )

        graph.add_node(
            "ticket_tool",
            self._ticket_node,
        )

        graph.add_node(
            "finalize",
            self._finalize_node,
        )

        # -------------------------------------------------
        # START
        # -------------------------------------------------

        graph.add_edge(
            START,
            "route",
        )

        # -------------------------------------------------
        # ROUTER EDGES
        # -------------------------------------------------

        graph.add_conditional_edges(
            "route",
            self._after_route,
            {
                "rag_tool": ("rag_tool"),
                "order_tool": ("order_tool"),
                "ticket_tool": ("ticket_tool"),
                "finalize": ("finalize"),
            },
        )

        # -------------------------------------------------
        # ORDER EDGES
        # -------------------------------------------------

        graph.add_conditional_edges(
            "order_tool",
            self._after_order,
            {
                "rag_tool": ("rag_tool"),
                "finalize": ("finalize"),
            },
        )

        # -------------------------------------------------
        # TOOL → FINALIZE
        # -------------------------------------------------

        graph.add_edge(
            "rag_tool",
            "finalize",
        )

        graph.add_edge(
            "ticket_tool",
            "finalize",
        )

        # -------------------------------------------------
        # END
        # -------------------------------------------------

        graph.add_edge(
            "finalize",
            END,
        )

        return graph.compile()

    # =====================================================
    # PUBLIC RUN METHOD
    # =====================================================

    def run(
        self,
        message: str,
    ) -> AgentChatResponse:
        """
        Execute one customer-support request.
        """

        message = message.strip()

        if not message:
            raise ValueError("Message cannot be empty")

        initial_state: SupportAgentState = {
            "user_input": (message),
            "tool_calls": [],
            "trajectory": [],
        }

        result = self.graph.invoke(initial_state)

        return AgentChatResponse(
            message=(message),
            intent=result.get(
                "intent",
                "unsupported",
            ),
            answer=result.get(
                "final_answer",
                "",
            ),
            tool_calls=result.get(
                "tool_calls",
                [],
            ),
            trajectory=result.get(
                "trajectory",
                [],
            ),
            task_completed=result.get(
                "task_completed",
                False,
            ),
            error=result.get("error"),
        )
