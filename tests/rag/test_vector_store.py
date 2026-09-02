def test_vector_database_contains_records(
    policy_vector_store,
):

    assert policy_vector_store.count() > 0


def test_refund_semantic_search(
    policy_vector_store,
):

    hits = policy_vector_store.search(
        query=("Can I return a product after twenty days?"),
        n_results=3,
    )

    assert hits

    assert hits[0].policy_id == "REFUND_POLICY"


def test_shipping_semantic_search(
    policy_vector_store,
):

    hits = policy_vector_store.search(
        query=("How many days does normal delivery take?"),
        n_results=3,
    )

    assert hits

    assert hits[0].policy_id == "SHIPPING_POLICY"


def test_password_semantic_search(
    policy_vector_store,
):

    hits = policy_vector_store.search(
        query=("I forgot my login password. What should I do?"),
        n_results=3,
    )

    assert hits

    assert hits[0].policy_id == "PASSWORD_POLICY"


def test_top_k(
    policy_vector_store,
):

    hits = policy_vector_store.search(
        query="business days",
        n_results=2,
    )

    assert len(hits) == 2


def test_metadata_filter(
    policy_vector_store,
):

    hits = policy_vector_store.search(
        query="business days",
        n_results=3,
        where={"policy_id": ("SHIPPING_POLICY")},
    )

    assert hits

    assert all(hit.policy_id == "SHIPPING_POLICY" for hit in hits)
