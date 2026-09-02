from __future__ import annotations

import json
from pathlib import Path

from app.rag.quality import (
    precision_at_k,
    recall_at_k,
    unique_in_order,
)

DATASET_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "retrieval_golden_dataset.json"
)


def load_dataset():

    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def test_retrieval_golden_dataset(
    policy_vector_store,
):

    dataset = load_dataset()

    passed = 0

    total_precision = 0.0
    total_recall = 0.0

    for case in dataset:
        hits = policy_vector_store.search(
            query=case["query"],
            n_results=3,
        )

        retrieved_policy_ids = unique_in_order([hit.policy_id for hit in hits])

        expected_policy_ids = case["expected_policy_ids"]

        precision = precision_at_k(
            retrieved=(retrieved_policy_ids),
            relevant=(expected_policy_ids),
            k=3,
        )

        recall = recall_at_k(
            retrieved=(retrieved_policy_ids),
            relevant=(expected_policy_ids),
            k=3,
        )

        total_precision += precision
        total_recall += recall

        top_result = retrieved_policy_ids[0] if retrieved_policy_ids else None

        expected_top = expected_policy_ids[0]

        if top_result == expected_top:
            passed += 1

        print()
        print(f"Case: {case['id']}")

        print(f"Query: {case['query']}")

        print(f"Expected: {expected_policy_ids}")

        print(f"Retrieved: {retrieved_policy_ids}")

        print(f"Precision@3: {precision:.2f}")

        print(f"Recall@3: {recall:.2f}")

    total = len(dataset)

    top1_accuracy = passed / total

    average_precision = total_precision / total

    average_recall = total_recall / total

    print()
    print("==================================")

    print("RETRIEVAL QUALITY REPORT")

    print("==================================")

    print(f"Total: {total}")

    print(f"Passed: {passed}")

    print(f"Top-1 Accuracy: {top1_accuracy:.2%}")

    print(f"Average Precision@3: {average_precision:.2f}")

    print(f"Average Recall@3: {average_recall:.2f}")

    print("==================================")

    assert top1_accuracy == 1.0

    assert average_recall == 1.0
