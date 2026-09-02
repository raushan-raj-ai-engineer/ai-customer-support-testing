from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)
from uuid import uuid4

from app.models import (
    TicketCreateRequest,
    TicketResponse,
    TicketStatus,
)


class TicketService:
    """
    In-memory ticket database for learning.

    Later this could become:

        PostgreSQL
        ServiceNow
        Jira
        Zendesk
        MCP ticket tool
    """

    def __init__(
        self,
    ) -> None:

        self._tickets: dict[
            str,
            TicketResponse,
        ] = {}

    # =====================================================
    # CREATE
    # =====================================================

    def create_ticket(
        self,
        request: TicketCreateRequest,
    ) -> TicketResponse:

        ticket_id = "TKT-" + uuid4().hex[:8].upper()

        ticket = TicketResponse(
            ticket_id=ticket_id,
            customer_name=(request.customer_name),
            email=request.email,
            category=(request.category),
            message=request.message,
            status=TicketStatus.OPEN,
            created_at=(datetime.now(timezone.utc)),
        )

        self._tickets[ticket_id] = ticket

        return ticket

    # =====================================================
    # GET
    # =====================================================

    def get_ticket(
        self,
        ticket_id: str,
    ) -> TicketResponse | None:

        normalized_id = ticket_id.strip().upper()

        return self._tickets.get(normalized_id)

    # =====================================================
    # RESET — TEST SUPPORT
    # =====================================================

    def reset(
        self,
    ) -> None:

        self._tickets.clear()


ticket_service = TicketService()
