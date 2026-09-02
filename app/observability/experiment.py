from __future__ import annotations

from typing import Any

from langsmith import Client

from app.observability.dataset import (
    LANGSMITH_DATASET_NAME,
)
from app.observability.evaluators import (
    build_langsmith_evaluators,
)
from app.observability.tracing import (
    run_traced_agent,
)

# =========================================================
# TARGET
# =========================================================


def agent_experiment_target(
    inputs: dict[str, Any],
) -> dict[str, Any]:
    """
    LangSmith passes Example.inputs here.

    We run the real support agent and convert
    its output into a stable experiment schema.
    """

    message = inputs.get("message")

    if not isinstance(
        message,
        str,
    ):
        raise TypeError("Experiment input 'message' must be a string.")

    result = run_traced_agent(message)

    tool_calls = result.get(
        "tool_calls",
        [],
    )

    tool_names: list[str] = []

    for call in tool_calls:
        if not isinstance(
            call,
            dict,
        ):
            continue

        name = call.get("name")

        if isinstance(
            name,
            str,
        ):
            tool_names.append(name)

    return {
        "intent": (result.get("intent")),
        "answer": (
            result.get(
                "answer",
                "",
            )
        ),
        "tool_names": (tool_names),
        "trajectory": (
            result.get(
                "trajectory",
                [],
            )
        ),
        "task_completed": (
            result.get(
                "task_completed",
                False,
            )
        ),
        "error": (result.get("error")),
    }


# =========================================================
# RUN EXPERIMENT
# =========================================================


def run_agent_experiment(
    client: Client,
):

    evaluators = build_langsmith_evaluators()

    return client.evaluate(
        agent_experiment_target,
        data=(LANGSMITH_DATASET_NAME),
        evaluators=evaluators,
        experiment_prefix=("support-agent-stage6"),
        description=(
            "Stage 6 LangSmith experiment "
            "for intent routing, tool sequence, "
            "task completion, required answer facts "
            "and approved-tool validation."
        ),
        max_concurrency=1,
        metadata={
            "stage": 6,
            "application": ("ai-customer-support-testing"),
            "generator_model": ("ollama:llama3.2"),
            "router_model": ("ollama:llama3.2"),
            "vector_store": ("chroma"),
            "embedding_model": ("all-MiniLM-L6-v2"),
            "evaluation_type": ("agent-regression"),
        },
    )
