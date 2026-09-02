from __future__ import annotations

import json
from pathlib import (
    Path,
)
from typing import (
    Any,
)

from langsmith import (
    Client,
)

# =========================================================
# CONSTANTS
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[2]


DATASET_PATH = PROJECT_ROOT / "config" / "agent_eval_dataset.json"


LANGSMITH_DATASET_NAME = "ai-customer-support-agent-v1"


# =========================================================
# LOCAL DATASET
# =========================================================


def load_agent_eval_dataset(
    path: Path = DATASET_PATH,
) -> list[dict[str, Any]]:

    raw = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(
        raw,
        list,
    ):
        raise TypeError("Agent evaluation dataset must be a list.")

    validated: list[dict[str, Any]] = []

    required_reference_fields = {
        "expected_intent",
        "expected_tools",
        "expected_task_completed",
        "answer_must_contain",
    }

    for item in raw:
        if not isinstance(
            item,
            dict,
        ):
            raise TypeError("Each dataset item must be an object.")

        if "id" not in item:
            raise ValueError("Dataset item missing id.")

        inputs = item.get("inputs")

        outputs = item.get("outputs")

        if not isinstance(
            inputs,
            dict,
        ):
            raise TypeError("Dataset inputs must be an object.")

        if not isinstance(
            outputs,
            dict,
        ):
            raise TypeError("Dataset outputs must be an object.")

        message = inputs.get("message")

        if (
            not isinstance(
                message,
                str,
            )
            or not message.strip()
        ):
            raise ValueError("Dataset message must be a non-empty string.")

        missing = required_reference_fields - outputs.keys()

        if missing:
            raise ValueError(
                f"Dataset reference output missing fields: {sorted(missing)}"
            )

        validated.append(item)

    return validated


# =========================================================
# LANGSMITH FORMAT
# =========================================================


def build_langsmith_examples() -> list[dict[str, Any]]:

    dataset = load_agent_eval_dataset()

    examples: list[dict[str, Any]] = []

    for case in dataset:
        examples.append({
            "inputs": (case["inputs"]),
            "outputs": (case["outputs"]),
            "metadata": {
                "case_id": (case["id"]),
                "stage": 6,
                "source": ("local-golden-dataset"),
            },
        })

    return examples


# =========================================================
# SYNC DATASET
# =========================================================


def sync_langsmith_dataset(
    client: Client,
    dataset_name: str = (LANGSMITH_DATASET_NAME),
) -> str:
    """
    Create dataset only if it does not already exist.

    We intentionally avoid silently adding duplicates.

    If the golden dataset changes materially,
    create v2 rather than mutating baseline history.
    """

    if client.has_dataset(dataset_name=dataset_name):
        return f"Dataset already exists: {dataset_name}"

    dataset = client.create_dataset(
        dataset_name=(dataset_name),
        description=(
            "Golden dataset for AI Customer Support LangGraph agent evaluation."
        ),
    )

    examples = build_langsmith_examples()

    client.create_examples(
        dataset_id=dataset.id,
        examples=examples,
    )

    return f"Created dataset: {dataset.name} with {len(examples)} examples"
