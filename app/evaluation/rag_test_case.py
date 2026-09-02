from __future__ import annotations

import json
from pathlib import Path

from deepeval.test_case import (
    LLMTestCase,
    RetrievedContextData,
)

from app.rag.models import (
    RAGResponse,
)

# =========================================================
# PROJECT PATHS
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[2]


DEFAULT_DATASET_PATH = PROJECT_ROOT / "config" / "rag_eval_dataset.json"


# =========================================================
# LOAD GOLDEN DATASET
# =========================================================


def load_rag_eval_dataset(
    dataset_path: Path = DEFAULT_DATASET_PATH,
) -> list[dict[str, str]]:
    """
    Load the golden RAG evaluation dataset.

    Each test case contains:

        id
        question
        expected_output
        expected_policy_id
    """

    data = json.loads(dataset_path.read_text(encoding="utf-8"))

    if not isinstance(
        data,
        list,
    ):
        raise TypeError("RAG evaluation dataset must be a list")

    validated_data: list[dict[str, str]] = []

    for item in data:
        if not isinstance(
            item,
            dict,
        ):
            raise TypeError("Each RAG evaluation case must be an object")

        required_fields = {
            "id",
            "question",
            "expected_output",
            "expected_policy_id",
        }

        missing_fields = required_fields - item.keys()

        if missing_fields:
            raise ValueError(
                "RAG evaluation case is "
                "missing required fields: "
                f"{sorted(missing_fields)}"
            )

        case: dict[
            str,
            str,
        ] = {}

        for key in required_fields:
            value = item[key]

            if not isinstance(
                value,
                str,
            ):
                raise TypeError(f"Field '{key}' must be a string")

            case[key] = value

        validated_data.append(case)

    return validated_data


# =========================================================
# BUILD DEEPEVAL TEST CASE
# =========================================================


def build_deepeval_test_case(
    response: RAGResponse,
    expected_output: str,
) -> LLMTestCase:
    """
    Convert our application's RAGResponse into
    a DeepEval LLMTestCase.

    Mapping:

        input
            → original customer question

        actual_output
            → actual generated RAG answer

        expected_output
            → golden expected answer

        retrieval_context
            → chunks actually retrieved by Chroma

    Important:

    DeepEval accepts retrieval_context as:

        list[str | RetrievedContextData]

    Our application returns:

        list[str]

    The explicit target type below prevents Pylance's
    list-invariance warning while preserving the actual
    runtime values.
    """

    retrieval_context: list[str | RetrievedContextData] = []

    retrieval_context.extend(response.retrieval_context)

    return LLMTestCase(
        input=response.question,
        actual_output=response.answer,
        expected_output=(expected_output),
        retrieval_context=(retrieval_context),
    )
