def test_create_support_ticket(
    client,
):

    payload = {
        "customer_name": ("Rohit Raj"),
        "email": ("rohit@example.com"),
        "category": "shipping",
        "message": ("My order has not arrived yet."),
    }

    response = client.post(
        "/api/v1/tickets",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["ticket_id"].startswith("TKT-")

    assert body["status"] == "OPEN"

    assert body["category"] == "shipping"

    assert body["message"] == payload["message"]


def test_created_ticket_can_be_retrieved(
    client,
):

    create_response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": ("Rohit Raj"),
            "email": ("rohit@example.com"),
            "category": "refund",
            "message": ("I want to return my laptop."),
        },
    )

    ticket_id = create_response.json()["ticket_id"]

    get_response = client.get(f"/api/v1/tickets/{ticket_id}")

    assert get_response.status_code == 200

    assert get_response.json()["ticket_id"] == ticket_id


def test_invalid_email_rejected(
    client,
):

    response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": ("Rohit Raj"),
            "email": "bad-email",
            "category": "refund",
            "message": ("I need help with my refund."),
        },
    )

    assert response.status_code == 422


def test_invalid_ticket_category_rejected(
    client,
):

    response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": ("Rohit Raj"),
            "email": ("rohit@example.com"),
            "category": ("something-random"),
            "message": ("This should fail validation."),
        },
    )

    assert response.status_code == 422


def test_unknown_ticket_returns_404(
    client,
):

    response = client.get("/api/v1/tickets/TKT-UNKNOWN")

    assert response.status_code == 404
