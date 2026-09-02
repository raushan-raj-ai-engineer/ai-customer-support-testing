from __future__ import annotations

from typing import Any

from langsmith.evaluation import (
    EvaluationResult,
    RunEvaluator,
    run_evaluator,
)
from langsmith.schemas import (
    Example,
    Run,
)

# =========================================================
# PURE HELPERS
#
# These are deterministic Python functions.
# Unit tests can call them directly.
# =========================================================


def _reference(
    reference_outputs: dict[str, Any] | None,
    key: str,
) -> Any:

    if reference_outputs is None:
        raise ValueError("reference_outputs are required.")

    if key not in reference_outputs:
        raise KeyError(f"Missing reference field: {key}")

    return reference_outputs[key]


# =========================================================
# PURE SCORE FUNCTIONS
# =========================================================


def score_intent_match(
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any],
) -> bool:

    expected = _reference(
        reference_outputs,
        "expected_intent",
    )

    actual = outputs.get("intent")

    return actual == expected


def score_tool_sequence_match(
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any],
) -> bool:

    expected = list(
        _reference(
            reference_outputs,
            "expected_tools",
        )
    )

    actual = list(
        outputs.get(
            "tool_names",
            [],
        )
    )

    return actual == expected


def score_task_completion_match(
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any],
) -> bool:

    expected = bool(
        _reference(
            reference_outputs,
            "expected_task_completed",
        )
    )

    actual = bool(
        outputs.get(
            "task_completed",
            False,
        )
    )

    return actual is expected


def score_answer_contains_required_facts(
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any],
) -> bool:

    required = list(
        _reference(
            reference_outputs,
            "answer_must_contain",
        )
    )

    answer = str(
        outputs.get(
            "answer",
            "",
        )
    ).lower()

    return all(str(fact).lower() in answer for fact in required)


def score_approved_tools_only(
    outputs: dict[str, Any],
) -> bool:

    allowed = {
        "rag_policy_lookup",
        "order_lookup",
        "ticket_create",
    }

    actual = set(
        outputs.get(
            "tool_names",
            [],
        )
    )

    return actual <= allowed


# =========================================================
# EXTRACT RUN / EXAMPLE DATA
# =========================================================


def _run_outputs(
    run: Run,
) -> dict[str, Any]:

    outputs = run.outputs

    if not isinstance(
        outputs,
        dict,
    ):
        return {}

    return outputs


def _reference_outputs(
    example: Example | None,
) -> dict[str, Any]:

    if example is None:
        raise ValueError("LangSmith evaluator requires a dataset Example.")

    outputs = example.outputs

    if not isinstance(
        outputs,
        dict,
    ):
        raise ValueError("Dataset example does not contain reference outputs.")

    return outputs


# =========================================================
# LANGSMITH RUN EVALUATORS
# =========================================================


@run_evaluator
def intent_match_evaluator(
    run: Run,
    example: Example | None = None,
) -> EvaluationResult:

    actual_outputs = _run_outputs(run)

    reference_outputs = _reference_outputs(example)

    score = score_intent_match(
        actual_outputs,
        reference_outputs,
    )

    return EvaluationResult(
        key="intent_match",
        score=score,
    )


@run_evaluator
def tool_sequence_match_evaluator(
    run: Run,
    example: Example | None = None,
) -> EvaluationResult:

    actual_outputs = _run_outputs(run)

    reference_outputs = _reference_outputs(example)

    score = score_tool_sequence_match(
        actual_outputs,
        reference_outputs,
    )

    return EvaluationResult(
        key="tool_sequence_match",
        score=score,
    )


@run_evaluator
def task_completion_match_evaluator(
    run: Run,
    example: Example | None = None,
) -> EvaluationResult:

    actual_outputs = _run_outputs(run)

    reference_outputs = _reference_outputs(example)

    score = score_task_completion_match(
        actual_outputs,
        reference_outputs,
    )

    return EvaluationResult(
        key="task_completion_match",
        score=score,
    )


@run_evaluator
def answer_required_facts_evaluator(
    run: Run,
    example: Example | None = None,
) -> EvaluationResult:

    actual_outputs = _run_outputs(run)

    reference_outputs = _reference_outputs(example)

    score = score_answer_contains_required_facts(
        actual_outputs,
        reference_outputs,
    )

    return EvaluationResult(
        key="answer_contains_required_facts",
        score=score,
    )


@run_evaluator
def approved_tools_only_evaluator(
    run: Run,
    example: Example | None = None,
) -> EvaluationResult:

    actual_outputs = _run_outputs(run)

    score = score_approved_tools_only(actual_outputs)

    return EvaluationResult(
        key="approved_tools_only",
        score=score,
    )


# =========================================================
# EXPLICIT TYPED EVALUATOR LIST
# =========================================================


def build_langsmith_evaluators() -> list[RunEvaluator]:

    return [
        intent_match_evaluator,
        tool_sequence_match_evaluator,
        task_completion_match_evaluator,
        answer_required_facts_evaluator,
        approved_tools_only_evaluator,
    ]
