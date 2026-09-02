from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# =========================================================
# ORDER MODELS
# =========================================================


class OrderStatus(str, Enum):
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderItem(BaseModel):
    name: str
    quantity: int = Field(gt=0)


class OrderResponse(BaseModel):
    order_id: str
    customer_name: str
    status: OrderStatus
    items: list[OrderItem]
    tracking_number: str | None = None
    estimated_delivery: str | None = None


# =========================================================
# SUPPORT TICKET MODELS
# =========================================================


class TicketCategory(str, Enum):
    REFUND = "refund"
    SHIPPING = "shipping"
    PASSWORD = "password"
    ORDER = "order"
    OTHER = "other"


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class TicketCreateRequest(BaseModel):
    customer_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: str = Field(
        min_length=5,
        max_length=200,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )

    category: TicketCategory

    message: str = Field(
        min_length=10,
        max_length=2000,
    )


class TicketResponse(BaseModel):
    ticket_id: str
    customer_name: str
    email: str
    category: TicketCategory
    message: str
    status: TicketStatus
    created_at: datetime


# =========================================================
# KNOWLEDGE / POLICY
# =========================================================


class PolicyResponse(BaseModel):
    policy_id: str
    title: str
    content: str


# =========================================================
# AI / RAG API MODELS
# =========================================================


class AIQuestionRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
    )


class AIAnswerResponse(BaseModel):
    question: str

    answer: str

    retrieved_policy_ids: list[str]
