from __future__ import annotations

import os

import pytest
from deepeval import (
    assert_test,
)

from app.evaluation.rag_metrics import (
    build_business_correctness_metric,
    core_rag_metric_list,
)
from app.evaluation.rag_test_case import (
    build_deepeval_test_case,
    load_rag_eval_dataset,
)
from app.rag.rag_service import (
    RAGService,
)

# =========================================================
# MARKERS
# =========================================================


pytestmark = [
    pytest.mark.live_llm,
    pytest.mark.deepeval,
]


RUN_DEEPEVAL = (
    os.getenv(
        "RUN_DEEPEVAL",
        "0",
    )
    == "1"
)


# =========================================================
# FIXTURES
# =========================================================


@pytest.fixture(scope="module")
def rag_service():

    return RAGService()


# =========================================================
# PARAMETERIZED DATASET
# =========================================================


@pytest.mark.skipif(
    not RUN_DEEPEVAL,
    reason=("Set RUN_DEEPEVAL=1 to run DeepEval tests"),
)
@pytest.mark.parametrize(
    "case",
    load_rag_eval_dataset(),
    ids=lambda case: case["id"],
)
def test_rag_quality_gate(
    rag_service,
    case,
):

    # -----------------------------------------------------
    # ACTUAL APPLICATION EXECUTION
    # -----------------------------------------------------

    response = rag_service.ask(case["question"])

    print()
    print("=" * 70)

    print(f"CASE: {case['id']}")

    print(f"Question: {case['question']}")

    print(f"Expected Policy: {case['expected_policy_id']}")

    print(f"Retrieved Policies: {response.retrieved_policy_ids}")

    print(f"Answer:\n{response.answer}")

    # -----------------------------------------------------
    # HARD DETERMINISTIC RETRIEVAL GATE
    # -----------------------------------------------------

    assert response.retrieved_policy_ids

    assert response.retrieved_policy_ids[0] == case["expected_policy_id"]

    # -----------------------------------------------------
    # BUILD DEEPEVAL TEST CASE
    # -----------------------------------------------------

    test_case = build_deepeval_test_case(
        response=response,
        expected_output=(case["expected_output"]),
    )

    # -----------------------------------------------------
    # CORE RAG QUALITY
    # -----------------------------------------------------

    assert_test(
        test_case=test_case,
        metrics=(core_rag_metric_list()),
        run_async=False,
    )

    # -----------------------------------------------------
    # BUSINESS CORRECTNESS
    # -----------------------------------------------------

    assert_test(
        test_case=test_case,
        metrics=[build_business_correctness_metric()],
        run_async=False,
    )
