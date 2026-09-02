from app.agent.router import (
    SupportIntentRouter,
    extract_order_id,
)


def router() -> SupportIntentRouter:

    return SupportIntentRouter(use_llm=False)


def test_extract_order_id():

    assert extract_order_id("Where is ORD-1001?") == "ORD-1001"


def test_policy_routing():

    decision = router().route("How long does standard shipping take?")

    assert decision.intent == "policy"


def test_order_routing():

    decision = router().route("Where is ORD-1001?")

    assert decision.intent == "order"

    assert decision.order_id == "ORD-1001"


def test_ticket_routing():

    decision = router().route("Create a ticket because my order is delayed.")

    assert decision.intent == "ticket"


def test_order_policy_routing():

    decision = router().route("Can I return ORD-1001?")

    assert decision.intent == "order_policy"

    assert decision.order_id == "ORD-1001"


def test_unsupported_routing():

    decision = router().route("Tell me a joke.")

    assert decision.intent == "unsupported"
