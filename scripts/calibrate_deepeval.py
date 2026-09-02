from __future__ import annotations

from deepeval.metrics import (
    FaithfulnessMetric,
)
from deepeval.test_case import (
    LLMTestCase,
)

from app.evaluation.model import (
    get_evaluation_model,
)


def run_case(
    name: str,
    actual_output: str,
) -> None:

    metric = FaithfulnessMetric(
        threshold=0.80,
        model=(get_evaluation_model()),
        include_reason=True,
        async_mode=False,
    )

    test_case = LLMTestCase(
        input=("How long does standard shipping take?"),
        actual_output=actual_output,
        retrieval_context=[("Standard shipping normally takes 3 to 5 business days.")],
    )

    metric.measure(test_case)

    print()
    print("=" * 70)

    print(name)

    print("=" * 70)

    print(f"Output: {actual_output}")

    print(f"Score: {metric.score}")

    print(f"Reason: {metric.reason}")


def main() -> None:

    run_case(
        name="KNOWN GOOD ANSWER",
        actual_output=("Standard shipping normally takes 3 to 5 business days."),
    )

    run_case(
        name="KNOWN BAD ANSWER",
        actual_output=("Standard shipping always arrives within 24 hours."),
    )


if __name__ == "__main__":
    main()
