from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import (
    router as api_router,
)
from app.ui import (
    WEB_DIR,
)
from app.ui import (
    router as ui_router,
)

# =========================================================
# FASTAPI APPLICATION
# =========================================================


app = FastAPI(
    title=("AI Customer Support Testing Platform"),
    version="1.0.0",
    description=(
        "Production-style AI customer-support "
        "application with RAG, LangGraph, "
        "DeepEval, LangSmith, guardrails, "
        "Playwright and MCP testing."
    ),
)


# =========================================================
# API ROUTES
# =========================================================


app.include_router(api_router)


# =========================================================
# UI ROUTES
# =========================================================


app.include_router(ui_router)


# =========================================================
# STATIC FILES
# =========================================================


app.mount(
    "/static",
    StaticFiles(directory=(WEB_DIR / "static")),
    name="static",
)


# =========================================================
# HEALTH
# =========================================================


@app.get(
    "/",
    tags=["system"],
)
def root() -> dict[str, str]:

    return {
        "service": ("AI Customer Support Testing Platform"),
        "status": "running",
        "support_ui": "/support",
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["system"],
)
def health() -> dict[str, str]:
    """
    Application health endpoint.

    Preserves the original Stage 1 API contract.
    """

    return {
        "status": "UP",
        "service": "ai-customer-support",
    }
