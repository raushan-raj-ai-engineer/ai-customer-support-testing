from __future__ import annotations

import pytest

from app.security.dataset import (
    load_security_dataset,
)
from app.security.input_guard import (
    InputGuard,
)


def test_security_dataset_not_empty():

    dataset = load_security_dataset()

    assert dataset


def test_security_dataset_ids_unique():

    dataset = load_security_dataset()

    ids = [case["id"] for case in dataset]

    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "case",
    load_security_dataset(),
    ids=lambda case: case["id"],
)
def test_adversarial_security_gate(
    case,
):

    result = InputGuard().inspect(case["message"])

    assert result.allowed is case["expected_allowed"]
