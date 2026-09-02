from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


SECURITY_DATASET_PATH = PROJECT_ROOT / "config" / "security_adversarial_dataset.json"


def load_security_dataset(
    path: Path = (SECURITY_DATASET_PATH),
) -> list[dict[str, Any]]:

    raw = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(
        raw,
        list,
    ):
        raise TypeError("Security dataset must contain a JSON list.")

    validated: list[dict[str, Any]] = []

    ids: set[str] = set()

    for case in raw:
        if not isinstance(
            case,
            dict,
        ):
            raise TypeError("Each security case must be an object.")

        case_id = case.get("id")

        message = case.get("message")

        expected_allowed = case.get("expected_allowed")

        if not isinstance(
            case_id,
            str,
        ):
            raise TypeError("Security case id must be a string.")

        if case_id in ids:
            raise ValueError(f"Duplicate security case id: {case_id}")

        ids.add(case_id)

        if not isinstance(
            message,
            str,
        ):
            raise TypeError("Security case message must be a string.")

        if not isinstance(
            expected_allowed,
            bool,
        ):
            raise TypeError("expected_allowed must be boolean.")

        validated.append(case)

    return validated
