from __future__ import annotations

from app.security.dataset import (
    load_security_dataset,
)
from app.security.input_guard import (
    InputGuard,
)


def main() -> None:

    dataset = load_security_dataset()

    guard = InputGuard()

    total = len(dataset)

    passed = 0

    failures: list[str] = []

    print()
    print("=" * 70)

    print("STAGE 7 SECURITY QUALITY GATE")

    print("=" * 70)

    for case in dataset:
        result = guard.inspect(case["message"])

        expected = case["expected_allowed"]

        actual = result.allowed

        success = actual is expected

        if success:
            passed += 1

            status = "PASS"

        else:
            status = "FAIL"

            failures.append(case["id"])

        print(
            f"{status:4} "
            f"{case['id']:30} "
            f"expected_allowed="
            f"{expected} "
            f"actual_allowed="
            f"{actual}"
        )

    pass_rate = passed / total if total else 0.0

    print()
    print("-" * 70)

    print(f"Total:     {total}")

    print(f"Passed:    {passed}")

    print(f"Failed:    {len(failures)}")

    print(f"Pass rate: {pass_rate:.2%}")

    print("=" * 70)

    # -----------------------------------------------------
    # SECURITY HARD GATE
    # -----------------------------------------------------

    if failures:
        raise AssertionError(f"Security quality gate failed: {failures}")

    if pass_rate < 1.0:
        raise AssertionError(
            "Security quality gate requires 100% deterministic pass rate."
        )

    print("SECURITY QUALITY GATE: PASSED")


if __name__ == "__main__":
    main()
