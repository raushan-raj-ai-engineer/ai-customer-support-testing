from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

WEB_DIR = Path(__file__).resolve().parent / "web"


router = APIRouter()


@router.get(
    "/support",
    include_in_schema=False,
)
def support_page() -> FileResponse:
    """
    Serve the customer-support browser UI.
    """

    return FileResponse(WEB_DIR / "index.html")
