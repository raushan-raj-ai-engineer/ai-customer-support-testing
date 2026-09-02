def test_refund_policy(
    client,
):

    response = client.get("/api/v1/policies/refund")

    assert response.status_code == 200

    body = response.json()

    assert body["policy_id"] == "REFUND_POLICY"

    assert "30 days" in body["content"]

    assert "5 to 7 business days" in body["content"]


def test_shipping_policy(
    client,
):

    response = client.get("/api/v1/policies/shipping")

    assert response.status_code == 200

    body = response.json()

    assert body["policy_id"] == "SHIPPING_POLICY"

    assert "3 to 5 business days" in body["content"]


def test_password_policy(
    client,
):

    response = client.get("/api/v1/policies/password")

    assert response.status_code == 200

    body = response.json()

    assert body["policy_id"] == "PASSWORD_POLICY"

    assert "15 minutes" in body["content"]


def test_unknown_policy_returns_404(
    client,
):

    response = client.get("/api/v1/policies/random")

    assert response.status_code == 404
