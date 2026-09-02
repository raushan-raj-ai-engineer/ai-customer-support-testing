from __future__ import annotations

from typing import Any

# =========================================================
# FAKE ORDER DATABASE
#
# Later this could be:
#
# PostgreSQL
# MongoDB
# External Order API
# =========================================================


ORDERS: dict[str, dict[str, Any]] = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_name": "Rohit Raj",
        "status": "SHIPPED",
        "items": [
            {
                "name": "Laptop",
                "quantity": 1,
            }
        ],
        "tracking_number": "TRK-90001",
        "estimated_delivery": "2026-09-05",
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_name": "Amit Kumar",
        "status": "PROCESSING",
        "items": [
            {
                "name": "Wireless Mouse",
                "quantity": 2,
            }
        ],
        "tracking_number": None,
        "estimated_delivery": "2026-09-08",
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_name": "Neha Singh",
        "status": "DELIVERED",
        "items": [
            {
                "name": "Mechanical Keyboard",
                "quantity": 1,
            }
        ],
        "tracking_number": "TRK-90003",
        "estimated_delivery": None,
    },
}


# =========================================================
# POLICY CONFIGURATION
# =========================================================


POLICIES = {
    "refund": {
        "policy_id": "REFUND_POLICY",
        "title": "Refund and Return Policy",
        "filename": "refund_policy.md",
    },
    "shipping": {
        "policy_id": "SHIPPING_POLICY",
        "title": "Shipping Policy",
        "filename": "shipping_policy.md",
    },
    "password": {
        "policy_id": "PASSWORD_POLICY",
        "title": "Password and Account Security Policy",
        "filename": "password_policy.md",
    },
}
