from __future__ import annotations

import pytest

from app.security.tool_policy import (
    ToolAuthorizationError,
    ToolPolicy,
)


def policy() -> ToolPolicy:

    return ToolPolicy()


def test_policy_intent_allows_only_rag():

    policy().authorize(
        intent="policy",
        tool_name=("rag_policy_lookup"),
        arguments={"question": ("How long does shipping take?")},
        executed_tools=[],
        approve_write=False,
    )


def test_order_cannot_call_rag_first():

    with pytest.raises(ToolAuthorizationError):
        policy().authorize(
            intent="order",
            tool_name=("rag_policy_lookup"),
            arguments={"question": ("Where is order?")},
            executed_tools=[],
            approve_write=False,
        )


def test_order_policy_requires_correct_sequence():

    security = policy()

    security.authorize(
        intent="order_policy",
        tool_name=("order_lookup"),
        arguments={"order_id": ("ORD-1001")},
        executed_tools=[],
        approve_write=False,
    )

    security.authorize(
        intent="order_policy",
        tool_name=("rag_policy_lookup"),
        arguments={"question": ("What is the return policy?")},
        executed_tools=["order_lookup"],
        approve_write=False,
    )


def test_invalid_order_id_blocked():

    with pytest.raises(ToolAuthorizationError):
        policy().authorize(
            intent="order",
            tool_name=("order_lookup"),
            arguments={"order_id": ("../../etc/passwd")},
            executed_tools=[],
            approve_write=False,
        )


def test_ticket_write_requires_approval():

    with pytest.raises(ToolAuthorizationError):
        policy().authorize(
            intent="ticket",
            tool_name=("ticket_create"),
            arguments={
                "description": ("My order is delayed."),
                "order_id": None,
            },
            executed_tools=[],
            approve_write=False,
        )


def test_ticket_write_allowed_with_approval():

    policy().authorize(
        intent="ticket",
        tool_name=("ticket_create"),
        arguments={
            "description": ("My order is delayed."),
            "order_id": None,
        },
        executed_tools=[],
        approve_write=True,
    )


def test_unknown_tool_is_blocked():

    with pytest.raises(ToolAuthorizationError):
        policy().validate_arguments(
            tool_name=("delete_customer_account"),
            arguments={},
        )


def test_duplicate_tool_call_blocked():

    with pytest.raises(ToolAuthorizationError):
        policy().authorize(
            intent="order",
            tool_name=("order_lookup"),
            arguments={"order_id": ("ORD-1001")},
            executed_tools=["order_lookup"],
            approve_write=False,
        )
