from __future__ import annotations

from functools import lru_cache

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.agent.models import (
    AgentChatRequest,
    AgentChatResponse,
)
from app.agent.workflow import (
    SupportAgent,
)
from app.knowledge import (
    load_policy,
)
from app.models import (
    AIAnswerResponse,
    AIQuestionRequest,
    OrderResponse,
    PolicyResponse,
    TicketCreateRequest,
    TicketResponse,
)
from app.rag.rag_service import (
    RAGService,
)
from app.security.models import (
    SecureAgentChatRequest,
    SecureAgentChatResponse,
)
from app.security.secure_agent import (
    SecureSupportAgent,
)
from app.services.order_service import (
    order_service,
)
from app.services.ticket_service import (
    ticket_service,
)

router = APIRouter(prefix="/api/v1")


@lru_cache(maxsize=1)
def get_secure_support_agent() -> SecureSupportAgent:

    return SecureSupportAgent()


# =========================================================
# LAZY RAG SERVICE
# =========================================================


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:

    return RAGService()


# =========================================================
# LAZY LANGGRAPH AGENT
# =========================================================


@lru_cache(maxsize=1)
def get_support_agent() -> SupportAgent:

    return SupportAgent()


# =========================================================
# ORDER API
# =========================================================


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: str,
) -> OrderResponse:

    order = order_service.get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=(f"Order '{order_id}' was not found"),
        )

    return order


# =========================================================
# CREATE TICKET
# =========================================================


@router.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=(status.HTTP_201_CREATED),
)
def create_ticket(
    request: TicketCreateRequest,
) -> TicketResponse:

    return ticket_service.create_ticket(request)


# =========================================================
# GET TICKET
# =========================================================


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: str,
) -> TicketResponse:

    ticket = ticket_service.get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=(f"Ticket '{ticket_id}' was not found"),
        )

    return ticket


# =========================================================
# POLICY API
# =========================================================


@router.get(
    "/policies/{policy_name}",
    response_model=PolicyResponse,
)
def get_policy(
    policy_name: str,
) -> PolicyResponse:

    policy = load_policy(policy_name)

    if policy is None:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=(f"Policy '{policy_name}' was not found"),
        )

    return policy


# =========================================================
# DIRECT RAG API
# =========================================================


@router.post(
    "/ai/ask",
    response_model=AIAnswerResponse,
)
def ask_ai(
    request: AIQuestionRequest,
) -> AIAnswerResponse:

    service = get_rag_service()

    try:
        result = service.ask(request.question)

    except ValueError as exc:
        raise HTTPException(
            status_code=(status.HTTP_400_BAD_REQUEST),
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR),
            detail=(f"AI support service failed to process request: {exc}"),
        ) from exc

    return AIAnswerResponse(
        question=result.question,
        answer=result.answer,
        retrieved_policy_ids=(result.retrieved_policy_ids),
    )


# =========================================================
# LANGGRAPH AGENT API
# =========================================================


@router.post(
    "/agent/chat",
    response_model=AgentChatResponse,
)
def agent_chat(
    request: AgentChatRequest,
) -> AgentChatResponse:

    agent = get_support_agent()

    try:
        return agent.run(request.message)

    except ValueError as exc:
        raise HTTPException(
            status_code=(status.HTTP_400_BAD_REQUEST),
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR),
            detail=(f"Support agent failed: {exc}"),
        ) from exc


@router.post(
    "/secure-agent/chat",
    response_model=(SecureAgentChatResponse),
)
def secure_agent_chat(
    request: SecureAgentChatRequest,
) -> SecureAgentChatResponse:

    agent = get_secure_support_agent()

    try:
        return agent.run(
            request.message,
            approve_write=(request.approve_write),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(status.HTTP_400_BAD_REQUEST),
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=(status.HTTP_500_INTERNAL_SERVER_ERROR),
            detail=(f"Secure support agent failed: {exc}"),
        ) from exc
