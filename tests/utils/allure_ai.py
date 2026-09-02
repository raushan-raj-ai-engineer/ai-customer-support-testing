from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any

import allure


def _safe_json_value(
    value: Any,
) -> Any:
    if is_dataclass(value):
        return asdict(value)

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ) or value is None:
        return value

    if isinstance(value, dict):
        return {
            str(key): _safe_json_value(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            _safe_json_value(item)
            for item in value
        ]

    return str(value)


def attach_json(
    name: str,
    payload: Any,
) -> None:
    allure.attach(
        json.dumps(
            _safe_json_value(payload),
            indent=2,
            ensure_ascii=False,
        ),
        name=name,
        attachment_type=(
            allure.attachment_type.JSON
        ),
    )


def attach_ai_metric(
    *,
    metric_name: str,
    score: float | None,
    threshold: float | None,
    passed: bool | None = None,
    reason: str | None = None,
    evaluator_model: str | None = None,
) -> None:

    attach_json(
        f"AI Metric - {metric_name}",
        {
            "metric": metric_name,
            "score": score,
            "threshold": threshold,
            "passed": passed,
            "reason": reason,
            "evaluator_model": (
                evaluator_model
            ),
        },
    )

    if score is not None:
        allure.dynamic.parameter(
            f"{metric_name} score",
            score,
        )

    if threshold is not None:
        allure.dynamic.parameter(
            f"{metric_name} threshold",
            threshold,
        )
