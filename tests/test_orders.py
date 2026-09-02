def test_get_shipped_order(
    client,
):

    response = client.get("/api/v1/orders/ORD-1001")

    assert response.status_code == 200

    body = response.json()

    assert body["order_id"] == "ORD-1001"

    assert body["status"] == "SHIPPED"

    assert body["tracking_number"] == "TRK-90001"


def test_get_processing_order(
    client,
):

    response = client.get("/api/v1/orders/ORD-1002")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "PROCESSING"

    assert body["tracking_number"] is None


def test_order_id_is_case_insensitive(
    client,
):

    response = client.get("/api/v1/orders/ord-1001")

    assert response.status_code == 200

    assert response.json()["order_id"] == "ORD-1001"


def test_unknown_order_returns_404(
    client,
):

    response = client.get("/api/v1/orders/ORD-9999")

    assert response.status_code == 404

    assert "not found" in response.json()["detail"].lower()
