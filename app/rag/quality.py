from __future__ import annotations


def unique_in_order(
    values: list[str],
) -> list[str]:

    return list(dict.fromkeys(values))


def precision_at_k(
    retrieved: list[str],
    relevant: list[str],
    k: int,
) -> float:

    if k <= 0:
        raise ValueError("k must be greater than zero")

    top_k = retrieved[:k]

    if not top_k:
        return 0.0

    relevant_set = set(relevant)

    relevant_retrieved = sum(1 for item in top_k if item in relevant_set)

    return relevant_retrieved / len(top_k)


def recall_at_k(
    retrieved: list[str],
    relevant: list[str],
    k: int,
) -> float:

    if k <= 0:
        raise ValueError("k must be greater than zero")

    relevant_set = set(relevant)

    if not relevant_set:
        return 1.0

    top_k = set(retrieved[:k])

    relevant_retrieved = len(top_k & relevant_set)

    return relevant_retrieved / len(relevant_set)
