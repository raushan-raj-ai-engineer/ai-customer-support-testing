from app.evaluation.rag_test_case import (
    load_rag_eval_dataset,
)


def test_rag_eval_dataset_is_not_empty():

    dataset = load_rag_eval_dataset()

    assert dataset


def test_each_eval_case_has_required_fields():

    dataset = load_rag_eval_dataset()

    required_fields = {
        "id",
        "question",
        "expected_output",
        "expected_policy_id",
    }

    for case in dataset:
        assert required_fields.issubset(case.keys())


def test_eval_case_ids_are_unique():

    dataset = load_rag_eval_dataset()

    ids = [case["id"] for case in dataset]

    assert len(ids) == len(set(ids))


def test_expected_outputs_are_not_empty():

    dataset = load_rag_eval_dataset()

    for case in dataset:
        assert case["expected_output"].strip()
