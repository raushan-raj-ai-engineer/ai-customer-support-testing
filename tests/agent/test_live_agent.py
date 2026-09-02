from __future__ import annotations

import os

import pytest

from app.agent.workflow import (
    SupportAgent,
)

RUN_LIVE_AGENT = (
    os.getenv(
        "RUN_LIVE_AGENT",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.live_agent,
]


@pytest.fixture(scope="module")
def live_agent():

    return SupportAgent()


@pytest.mark.skipif(
    not RUN_LIVE_AGENT,
    reason=("Set RUN_LIVE_AGENT=1 to run live agent tests"),
)
def test_live_policy_agent(
    live_agent,
):

    result = live_agent.run("How long does standard shipping take?")

    print(result)

    assert result.intent == "policy"

    assert result.task_completed is True

    assert "3" in result.answer

    assert "5" in result.answer


@pytest.mark.skipif(
    not RUN_LIVE_AGENT,
    reason=("Set RUN_LIVE_AGENT=1 to run live agent tests"),
)
def test_live_order_agent(
    live_agent,
):

    result = live_agent.run("Where is ORD-1001?")

    print(result)

    assert result.intent == "order"

    assert result.task_completed is True

    assert any(call.name == "order_lookup" for call in result.tool_calls)


@pytest.mark.skipif(
    not RUN_LIVE_AGENT,
    reason=("Set RUN_LIVE_AGENT=1 to run live agent tests"),
)
def test_live_order_policy_agent(
    live_agent,
):

    result = live_agent.run("Can I return ORD-1001?")

    print(result)

    assert result.intent == "order_policy"

    tool_names = [call.name for call in result.tool_calls]

    assert tool_names == [
        "order_lookup",
        "rag_policy_lookup",
    ]
