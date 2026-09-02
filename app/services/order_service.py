from __future__ import annotations

from app.data import ORDERS
from app.models import OrderResponse


class OrderService:
    """
    Business/service layer for order operations.

    API route should not directly know where
    order data comes from.

    Later we can replace this with:

        real REST API
        database
        MCP tool
    """

    def get_order(
        self,
        order_id: str,
    ) -> OrderResponse | None:

        normalized_id = order_id.strip().upper()

        data = ORDERS.get(normalized_id)

        if data is None:
            return None

        return OrderResponse(**data)


order_service = OrderService()
