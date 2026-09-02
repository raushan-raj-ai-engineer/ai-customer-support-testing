from __future__ import annotations

from app.observability.evaluators import (
    build_langsmith_evaluators,
    score_answer_contains_required_facts,
    score_approved_tools_only,
    score_intent_match,
    score_task_completion_match,
    score_tool_sequence_match,
)

REFERENCE = {
    "expected_intent": ("order_policy"),
    "expected_tools": [
        "order_lookup",
        "rag_policy_lookup",
    ],
    "expected_task_completed": (True),
    "answer_must_contain": [
        "ORD-1001",
        "30",
    ],
}


GOOD_OUTPUT = {
    "intent": ("order_policy"),
    "answer": ("Order ORD-1001 is eligible under the 30-day policy."),
    "tool_names": [
        "order_lookup",
        "rag_policy_lookup",
    ],
    "task_completed": (True),
}


# =========================================================
# INTENT
# =========================================================


def test_intent_match_passes():

    assert score_intent_match(
        GOOD_OUTPUT,
        REFERENCE,
    )


def test_intent_match_detects_wrong_route():

    bad = dict(GOOD_OUTPUT)

    bad["intent"] = "policy"

    assert not (
        score_intent_match(
            bad,
            REFERENCE,
        )
    )


# =========================================================
# TOOL SEQUENCE
# =========================================================


def test_tool_sequence_match_passes():

    assert score_tool_sequence_match(
        GOOD_OUTPUT,
        REFERENCE,
    )


def test_tool_sequence_detects_wrong_order():

    bad = dict(GOOD_OUTPUT)

    bad["tool_names"] = [
        "rag_policy_lookup",
        "order_lookup",
    ]

    assert not (
        score_tool_sequence_match(
            bad,
            REFERENCE,
        )
    )


# =========================================================
# TASK COMPLETION
# =========================================================


def test_task_completion_passes():

    assert score_task_completion_match(
        GOOD_OUTPUT,
        REFERENCE,
    )


def test_task_completion_detects_failure():

    bad = dict(GOOD_OUTPUT)

    bad["task_completed"] = False

    assert not (
        score_task_completion_match(
            bad,
            REFERENCE,
        )
    )


# =========================================================
# ANSWER FACTS
# =========================================================


def test_answer_fact_gate_passes():

    assert score_answer_contains_required_facts(
        GOOD_OUTPUT,
        REFERENCE,
    )


def test_answer_fact_gate_detects_missing_fact():

    bad = dict(GOOD_OUTPUT)

    bad["answer"] = "Your order exists."

    assert not (
        score_answer_contains_required_facts(
            bad,
            REFERENCE,
        )
    )


# =========================================================
# APPROVED TOOLS
# =========================================================


def test_approved_tools_pass():

    assert score_approved_tools_only(GOOD_OUTPUT)


def test_unknown_tool_fails():

    bad = dict(GOOD_OUTPUT)

    bad["tool_names"] = [
        "order_lookup",
        "delete_customer_account",
    ]

    assert not (score_approved_tools_only(bad))


# =========================================================
# LANGSMITH WRAPPERS
# =========================================================


def test_langsmith_evaluator_bundle_created():

    evaluators = build_langsmith_evaluators()

    assert len(evaluators) == 5

    assert all(evaluator is not None for evaluator in evaluators)
