from __future__ import annotations

from app.observability.dataset import (
    build_langsmith_examples,
    load_agent_eval_dataset,
)


def test_agent_eval_dataset_not_empty():

    dataset = load_agent_eval_dataset()

    assert dataset


def test_agent_eval_ids_are_unique():

    dataset = load_agent_eval_dataset()

    ids = [case["id"] for case in dataset]

    assert len(ids) == len(set(ids))


def test_each_dataset_case_has_message():

    dataset = load_agent_eval_dataset()

    for case in dataset:
        message = case["inputs"]["message"]

        assert isinstance(
            message,
            str,
        )

        assert message.strip()


def test_langsmith_examples_created():

    examples = build_langsmith_examples()

    assert examples

    for example in examples:
        assert "inputs" in example

        assert "outputs" in example

        assert "metadata" in example
