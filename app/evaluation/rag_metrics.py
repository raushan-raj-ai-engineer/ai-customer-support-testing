from __future__ import annotations

from dataclasses import dataclass

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
    GEval,
)
from deepeval.test_case import (
    SingleTurnParams,
)

from app.evaluation.model import (
    get_evaluation_model,
)

# =========================================================
# THRESHOLDS
# =========================================================


FAITHFULNESS_THRESHOLD = 0.80

ANSWER_RELEVANCY_THRESHOLD = 0.80

CONTEXTUAL_RELEVANCY_THRESHOLD = 0.70

CONTEXTUAL_PRECISION_THRESHOLD = 0.70

CONTEXTUAL_RECALL_THRESHOLD = 0.80

BUSINESS_CORRECTNESS_THRESHOLD = 0.80


# =========================================================
# METRIC BUNDLE
# =========================================================


@dataclass
class RAGMetrics:
    faithfulness: FaithfulnessMetric

    answer_relevancy: AnswerRelevancyMetric

    contextual_relevancy: ContextualRelevancyMetric

    contextual_precision: ContextualPrecisionMetric

    contextual_recall: ContextualRecallMetric


# =========================================================
# BUILD CORE RAG METRICS
# =========================================================


def build_rag_metrics() -> RAGMetrics:

    model = get_evaluation_model()

    return RAGMetrics(
        faithfulness=FaithfulnessMetric(
            threshold=FAITHFULNESS_THRESHOLD,
            model=model,
            include_reason=True,
            async_mode=False,
        ),
        answer_relevancy=(
            AnswerRelevancyMetric(
                threshold=(ANSWER_RELEVANCY_THRESHOLD),
                model=model,
                include_reason=True,
                async_mode=False,
            )
        ),
        contextual_relevancy=(
            ContextualRelevancyMetric(
                threshold=(CONTEXTUAL_RELEVANCY_THRESHOLD),
                model=model,
                include_reason=True,
                async_mode=False,
            )
        ),
        contextual_precision=(
            ContextualPrecisionMetric(
                threshold=(CONTEXTUAL_PRECISION_THRESHOLD),
                model=model,
                include_reason=True,
                async_mode=False,
            )
        ),
        contextual_recall=(
            ContextualRecallMetric(
                threshold=(CONTEXTUAL_RECALL_THRESHOLD),
                model=model,
                include_reason=True,
                async_mode=False,
            )
        ),
    )


# =========================================================
# CORE METRIC LIST
# =========================================================


def core_rag_metric_list():

    metrics = build_rag_metrics()

    return [
        metrics.faithfulness,
        metrics.answer_relevancy,
        metrics.contextual_relevancy,
        metrics.contextual_precision,
        metrics.contextual_recall,
    ]


# =========================================================
# CUSTOM BUSINESS CORRECTNESS
# =========================================================


def build_business_correctness_metric() -> GEval:

    model = get_evaluation_model()

    return GEval(
        name=("Support Policy Correctness"),
        evaluation_steps=[
            ("Identify the core fact required by the customer's question."),
            ("Compare the actual output against the expected output."),
            ("Verify important policy numbers, durations, limits, and conditions."),
            (
                "Use retrieval context to determine "
                "whether additional details in the "
                "actual output are supported."
            ),
            (
                "Do not penalize accurate additional "
                "detail merely because the expected "
                "answer is shorter."
            ),
            (
                "Penalize contradictions, incorrect "
                "numbers, invented procedures, or "
                "unsupported claims."
            ),
        ],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
            SingleTurnParams.RETRIEVAL_CONTEXT,
        ],
        threshold=(BUSINESS_CORRECTNESS_THRESHOLD),
        model=model,
        async_mode=False,
    )
