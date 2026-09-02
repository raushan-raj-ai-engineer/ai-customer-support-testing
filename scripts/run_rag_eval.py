from __future__ import annotations

from app.evaluation.rag_metrics import (
    build_business_correctness_metric,
    build_rag_metrics,
)
from app.evaluation.rag_test_case import (
    build_deepeval_test_case,
    load_rag_eval_dataset,
)
from app.rag.rag_service import (
    RAGService,
)


def print_metric(
    name: str,
    metric,
) -> None:

    score = metric.score

    reason = getattr(
        metric,
        "reason",
        None,
    )

    threshold = metric.threshold

    passed = score is not None and score >= threshold

    print(f"{name}: {score:.2f} {'PASS' if passed else 'FAIL'}")

    if reason:
        print(f"Reason: {reason}")


def main() -> None:

    service = RAGService()

    dataset = load_rag_eval_dataset()

    passed_cases = 0

    print()
    print("=" * 80)

    print("STAGE 4 - RAG QUALITY EVALUATION")

    print("=" * 80)

    for case in dataset:
        print()
        print("-" * 80)

        print(f"CASE: {case['id']}")

        print(f"Question: {case['question']}")

        response = service.ask(case["question"])

        print(f"Expected Policy: {case['expected_policy_id']}")

        print(f"Retrieved Policies: {response.retrieved_policy_ids}")

        print(f"Answer: {response.answer}")

        deterministic_pass = (
            bool(response.retrieved_policy_ids)
            and response.retrieved_policy_ids[0] == case["expected_policy_id"]
        )

        print()

        print("Deterministic Retrieval: " + ("PASS" if deterministic_pass else "FAIL"))

        test_case = build_deepeval_test_case(
            response=response,
            expected_output=(case["expected_output"]),
        )

        metrics = build_rag_metrics()

        # =================================================
        # FAITHFULNESS
        # =================================================

        metrics.faithfulness.measure(test_case)

        print_metric(
            "Faithfulness",
            metrics.faithfulness,
        )

        # =================================================
        # ANSWER RELEVANCY
        # =================================================

        metrics.answer_relevancy.measure(test_case)

        print_metric(
            "Answer Relevancy",
            metrics.answer_relevancy,
        )

        # =================================================
        # CONTEXTUAL RELEVANCY
        # =================================================

        metrics.contextual_relevancy.measure(test_case)

        print_metric(
            "Contextual Relevancy",
            metrics.contextual_relevancy,
        )

        # =================================================
        # CONTEXTUAL PRECISION
        # =================================================

        metrics.contextual_precision.measure(test_case)

        print_metric(
            "Contextual Precision",
            metrics.contextual_precision,
        )

        # =================================================
        # CONTEXTUAL RECALL
        # =================================================

        metrics.contextual_recall.measure(test_case)

        print_metric(
            "Contextual Recall",
            metrics.contextual_recall,
        )

        # =================================================
        # BUSINESS CORRECTNESS
        # =================================================

        business = build_business_correctness_metric()

        business.measure(test_case)

        print_metric(
            "Business Correctness",
            business,
        )

        all_scores = [
            metrics.faithfulness.score,
            metrics.answer_relevancy.score,
            metrics.contextual_relevancy.score,
            metrics.contextual_precision.score,
            metrics.contextual_recall.score,
            business.score,
        ]

        score_pass = all(score is not None for score in all_scores)

        case_passed = (
            deterministic_pass
            and score_pass
            and metrics.faithfulness.is_successful()
            and metrics.answer_relevancy.is_successful()
            and metrics.contextual_relevancy.is_successful()
            and metrics.contextual_precision.is_successful()
            and metrics.contextual_recall.is_successful()
            and business.is_successful()
        )

        print()

        print("CASE RESULT: " + ("PASS" if case_passed else "FAIL"))

        if case_passed:
            passed_cases += 1

    print()
    print("=" * 80)

    print("FINAL RAG QUALITY REPORT")

    print("=" * 80)

    print(f"Total: {len(dataset)}")

    print(f"Passed: {passed_cases}")

    print(f"Failed: {len(dataset) - passed_cases}")

    pass_rate = passed_cases / len(dataset)

    print(f"Pass Rate: {pass_rate:.2%}")

    print("=" * 80)


if __name__ == "__main__":
    main()
