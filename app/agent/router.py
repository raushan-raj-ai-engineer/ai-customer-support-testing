from __future__ import annotations

import re
from typing import Any

from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_ollama import (
    ChatOllama,
)

from app.agent.models import (
    IntentDecision,
)

# =========================================================
# CONFIG
# =========================================================


DEFAULT_ROUTER_MODEL = "llama3.2"


# =========================================================
# ORDER ID
# =========================================================


ORDER_ID_PATTERN = re.compile(
    r"\bORD-\d+\b",
    re.IGNORECASE,
)


def extract_order_id(
    text: str,
) -> str | None:
    """
    Extract an order ID such as:

        ORD-1001
        ord-9999
    """

    match = ORDER_ID_PATTERN.search(text)

    if match is None:
        return None

    return match.group(0).upper()


# =========================================================
# DETERMINISTIC ROUTER
# =========================================================


def heuristic_route(
    message: str,
) -> IntentDecision:
    """
    High-confidence deterministic routing.

    Important design principle:

    Obvious business intents should not require
    an LLM decision.

    LLM routing is reserved for ambiguous requests.
    """

    text = message.strip().lower()

    order_id = extract_order_id(message)

    # =====================================================
    # TICKET
    # =====================================================

    ticket_words = (
        "create a ticket",
        "raise a ticket",
        "open a ticket",
        "create ticket",
        "raise ticket",
        "open ticket",
        "support ticket",
        "complaint",
    )

    if any(word in text for word in ticket_words):
        return IntentDecision(
            intent="ticket",
            order_id=order_id,
            ticket_description=(message.strip()),
            reason=("Customer explicitly requested a support ticket."),
        )

    # =====================================================
    # ORDER + POLICY
    # =====================================================

    order_policy_words = (
        "return",
        "refund",
        "eligible",
        "eligibility",
        "policy",
    )

    if order_id is not None and any(word in text for word in order_policy_words):
        return IntentDecision(
            intent="order_policy",
            order_id=order_id,
            reason=(
                "Request requires both "
                "order information and "
                "support-policy information."
            ),
        )

    # =====================================================
    # SPECIFIC ORDER LOOKUP
    # =====================================================

    if order_id is not None:
        return IntentDecision(
            intent="order",
            order_id=order_id,
            reason=("Customer is asking about a specific order."),
        )

    # =====================================================
    # POLICY
    # =====================================================

    policy_words = (
        "refund",
        "return",
        "shipping",
        "password",
        "reset",
        "policy",
        "how long",
        "eligible",
        "eligibility",
    )

    if any(word in text for word in policy_words):
        return IntentDecision(
            intent="policy",
            reason=("Customer is asking a support-policy question."),
        )

    # =====================================================
    # ORDER WITHOUT ORDER ID
    # =====================================================

    order_words = (
        "my order",
        "order status",
        "where is my order",
        "track my order",
        "tracking my order",
        "delivery status",
    )

    if any(word in text for word in order_words):
        return IntentDecision(
            intent="order",
            order_id=None,
            reason=("Customer is asking about order information."),
        )

    # =====================================================
    # UNSUPPORTED / AMBIGUOUS
    # =====================================================

    return IntentDecision(
        intent="unsupported",
        order_id=None,
        ticket_description=None,
        reason=("Request did not match a high-confidence deterministic route."),
    )


# =========================================================
# ROUTER PROMPT
# =========================================================


ROUTER_PROMPT = """
You are the routing component of a customer-support agent.

Classify the customer's message into exactly ONE intent.

Allowed intents:

policy
    Questions about refund, return, shipping,
    password or support policies.

order
    Questions about a specific order,
    order status, shipment, tracking or delivery.

ticket
    Customer explicitly wants to create,
    raise or open a support ticket or complaint.

order_policy
    The request requires BOTH:
    1. information about a specific order
    2. support-policy information

unsupported
    The request is outside supported capabilities.

Examples:

Customer:
How long does standard shipping take?

Intent:
policy


Customer:
Where is ORD-1001?

Intent:
order


Customer:
Where is ORD-9999?

Intent:
order


Customer:
Can I return ORD-1001?

Intent:
order_policy


Customer:
Create a ticket because my order is delayed.

Intent:
ticket


Customer:
Tell me a joke.

Intent:
unsupported


STRICT RULES:

1. Extract an order ID only when it exists
   in the customer message.

2. Order IDs look like:

   ORD-1001

3. Never invent an order ID.

4. Merely mentioning an order does not mean
   order_policy.

5. Use order_policy only when BOTH actual order
   information and policy information are needed.

6. For ticket requests, preserve the customer's
   issue in ticket_description.

7. Return only the requested structured output.


CUSTOMER MESSAGE:

{message}
""".strip()


# =========================================================
# ROUTER
# =========================================================


class SupportIntentRouter:
    """
    Hybrid deterministic + LLM router.

    High-confidence business routing:
        deterministic

    Ambiguous requests:
        LLM

    Structured-output failure:
        deterministic safe fallback
    """

    def __init__(
        self,
        model_name: str = DEFAULT_ROUTER_MODEL,
        use_llm: bool = True,
    ) -> None:

        self.use_llm = use_llm

        self.model_name = model_name

        self._chain: Any | None = None

    # =====================================================
    # BUILD LLM ROUTER
    # =====================================================

    def _get_chain(
        self,
    ) -> Any:

        if self._chain is not None:
            return self._chain

        prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)

        llm = ChatOllama(
            model=self.model_name,
            temperature=0,
        )

        structured_llm = llm.with_structured_output(IntentDecision)

        self._chain = prompt | structured_llm

        return self._chain

    # =====================================================
    # PUBLIC ROUTING METHOD
    # =====================================================

    def route(
        self,
        message: str,
    ) -> IntentDecision:
        """
        Route one customer message.

        Strategy:

        1. Run deterministic business rules.
        2. If intent is high-confidence, return it.
        3. Otherwise use the LLM for ambiguity.
        4. Fall back safely if LLM routing fails.
        """

        message = message.strip()

        if not message:
            raise ValueError("Message cannot be empty")

        # =================================================
        # STEP 1
        # HIGH-CONFIDENCE DETERMINISTIC ROUTING
        # =================================================

        deterministic = heuristic_route(message)

        if deterministic.intent != "unsupported":
            return deterministic

        # =================================================
        # STEP 2
        # NON-LLM / TEST MODE
        # =================================================

        if not self.use_llm:
            return deterministic

        # =================================================
        # STEP 3
        # LLM FOR AMBIGUOUS REQUESTS
        # =================================================

        try:
            chain = self._get_chain()

            result = chain.invoke({"message": message})

            if isinstance(
                result,
                IntentDecision,
            ):
                decision = result

            else:
                decision = IntentDecision.model_validate(result)

            # =============================================
            # ORDER ID GROUNDING
            # =============================================

            actual_order_id = extract_order_id(message)

            # If there is no order ID in the customer's
            # message, do not allow the LLM to invent one.
            if actual_order_id is None:
                decision.order_id = None

            else:
                decision.order_id = actual_order_id

            # =============================================
            # TICKET DESCRIPTION GROUNDING
            # =============================================

            if decision.intent == "ticket" and not decision.ticket_description:
                decision.ticket_description = message

            return decision

        except Exception:
            # =============================================
            # SAFE FALLBACK
            # =============================================

            return deterministic
