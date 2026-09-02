from __future__ import annotations

from enum import Enum
from typing import (
    Any,
    Callable,
    Literal,
    get_args,
    get_origin,
)

from app.models import (
    TicketCreateRequest,
)
from app.rag.rag_service import (
    RAGService,
)
from app.services.order_service import (
    order_service,
)
from app.services.ticket_service import (
    ticket_service,
)

# =========================================================
# SERIALIZATION
# =========================================================


def serialize_object(
    value: Any,
) -> dict[str, Any]:

    if value is None:
        return {}

    if hasattr(
        value,
        "model_dump",
    ):
        result = value.model_dump()

        if isinstance(
            result,
            dict,
        ):
            return result

    if isinstance(
        value,
        dict,
    ):
        return value

    if hasattr(
        value,
        "__dict__",
    ):
        return dict(value.__dict__)

    return {"value": str(value)}


# =========================================================
# ORDER TOOL
# =========================================================


def default_order_lookup(
    order_id: str,
) -> dict[str, Any] | None:

    order = order_service.get_order(order_id)

    if order is None:
        return None

    return serialize_object(order)


# =========================================================
# TICKET REQUEST ADAPTER
# =========================================================


def _literal_default(
    annotation: Any,
    preferred: str | None = None,
) -> Any | None:

    origin = get_origin(annotation)

    if origin is Literal:
        values = get_args(annotation)

        if preferred is not None and preferred in values:
            return preferred

        if values:
            return values[0]

    return None


def _enum_default(
    annotation: Any,
    preferred: str | None = None,
) -> Any | None:

    if not isinstance(
        annotation,
        type,
    ):
        return None

    try:
        if not issubclass(
            annotation,
            Enum,
        ):
            return None

    except TypeError:
        return None

    members = list(annotation)

    if not members:
        return None

    if preferred:
        for member in members:
            if str(member.value).upper() == preferred.upper():
                return member.value

    return members[0].value


def _default_required_value(
    field_name: str,
    annotation: Any,
    description: str,
    order_id: str | None,
) -> Any:

    name = field_name.lower()

    # -----------------------------------------------------
    # COMMON SUPPORT FIELDS
    # -----------------------------------------------------

    if name in {
        "description",
        "issue",
        "message",
        "details",
        "reason",
    }:
        return description

    if "description" in name or "issue" in name or "message" in name:
        return description

    if "subject" in name or "title" in name:
        return "AI customer support request"

    if "order" in name and "id" in name:
        return order_id or "UNKNOWN"

    if "email" in name:
        return "customer@example.com"

    if "customer" in name and "name" in name:
        return "AI Customer"

    if "priority" in name:
        literal_value = _literal_default(
            annotation,
            "MEDIUM",
        )

        if literal_value is not None:
            return literal_value

        enum_value = _enum_default(
            annotation,
            "MEDIUM",
        )

        if enum_value is not None:
            return enum_value

        return "MEDIUM"

    if "category" in name:
        literal_value = _literal_default(annotation)

        if literal_value is not None:
            return literal_value

        enum_value = _enum_default(annotation)

        if enum_value is not None:
            return enum_value

        return "GENERAL"

    # -----------------------------------------------------
    # GENERIC Pydantic REQUIRED FIELD SUPPORT
    # -----------------------------------------------------

    literal_value = _literal_default(annotation)

    if literal_value is not None:
        return literal_value

    enum_value = _enum_default(annotation)

    if enum_value is not None:
        return enum_value

    if annotation is str:
        return "AI support request"

    if annotation is int:
        return 0

    if annotation is float:
        return 0.0

    if annotation is bool:
        return False

    raise ValueError(
        "Agent could not automatically populate "
        f"required TicketCreateRequest field "
        f"'{field_name}'."
    )


def build_ticket_request(
    description: str,
    order_id: str | None = None,
) -> TicketCreateRequest:
    """
    Adapter around the existing Stage-1
    TicketCreateRequest model.

    This keeps the agent decoupled from small DTO
    differences such as issue vs description.
    """

    payload: dict[
        str,
        Any,
    ] = {}

    for (
        field_name,
        field_info,
    ) in TicketCreateRequest.model_fields.items():
        if not (field_info.is_required()):
            # We still populate useful optional fields
            # when their names are known.

            name = field_name.lower()

            if "order" in name and "id" in name and order_id:
                payload[field_name] = order_id

            continue

        payload[field_name] = _default_required_value(
            field_name=(field_name),
            annotation=(field_info.annotation),
            description=(description),
            order_id=(order_id),
        )

    return TicketCreateRequest.model_validate(payload)


# =========================================================
# TICKET TOOL
# =========================================================


def default_ticket_creator(
    description: str,
    order_id: str | None = None,
) -> dict[str, Any]:

    request = build_ticket_request(
        description=description,
        order_id=order_id,
    )

    ticket = ticket_service.create_ticket(request)

    return serialize_object(ticket)


# =========================================================
# TOOL COLLECTION
# =========================================================


class SupportTools:
    def __init__(
        self,
        rag_service: (RAGService | None) = None,
        order_lookup: (
            Callable[
                [str],
                dict[
                    str,
                    Any,
                ]
                | None,
            ]
            | None
        ) = None,
        ticket_creator: (
            Callable[
                [
                    str,
                    str | None,
                ],
                dict[
                    str,
                    Any,
                ],
            ]
            | None
        ) = None,
    ) -> None:

        self.rag_service = rag_service or RAGService()

        self.order_lookup = order_lookup or default_order_lookup

        self.ticket_creator = ticket_creator or default_ticket_creator

    # =====================================================
    # RAG TOOL
    # =====================================================

    def rag(
        self,
        question: str,
    ) -> dict[str, Any]:

        response = self.rag_service.ask(question)

        return {
            "answer": (response.answer),
            "retrieved_policy_ids": (response.retrieved_policy_ids),
            "retrieval_context": (response.retrieval_context),
        }

    # =====================================================
    # ORDER TOOL
    # =====================================================

    def order(
        self,
        order_id: str,
    ) -> (
        dict[
            str,
            Any,
        ]
        | None
    ):

        return self.order_lookup(order_id)

    # =====================================================
    # TICKET TOOL
    # =====================================================

    def ticket(
        self,
        description: str,
        order_id: str | None = None,
    ) -> dict[str, Any]:

        return self.ticket_creator(
            description,
            order_id,
        )
