from __future__ import annotations

import os
from dataclasses import dataclass

# =========================================================
# DEFAULTS
# =========================================================


DEFAULT_LANGSMITH_PROJECT = "ai-customer-support-agent-stage6"


# =========================================================
# BOOLEAN PARSING
# =========================================================


def parse_bool(
    value: str | None,
) -> bool:

    if value is None:
        return False

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


# =========================================================
# SETTINGS
# =========================================================


@dataclass(frozen=True)
class LangSmithSettings:
    tracing_enabled: bool

    api_key_configured: bool

    project: str

    endpoint: str | None

    workspace_id: str | None


# =========================================================
# READ SETTINGS
# =========================================================


def get_langsmith_settings() -> LangSmithSettings:

    api_key = os.getenv("LANGSMITH_API_KEY")

    project = os.getenv(
        "LANGSMITH_PROJECT",
        DEFAULT_LANGSMITH_PROJECT,
    )

    endpoint = os.getenv("LANGSMITH_ENDPOINT")

    workspace_id = os.getenv("LANGSMITH_WORKSPACE_ID")

    tracing_enabled = parse_bool(os.getenv("LANGSMITH_TRACING"))

    return LangSmithSettings(
        tracing_enabled=(tracing_enabled),
        api_key_configured=bool(api_key and api_key.strip()),
        project=project,
        endpoint=endpoint,
        workspace_id=(workspace_id),
    )


# =========================================================
# VALIDATE
# =========================================================


def validate_langsmith_settings(
    require_tracing: bool = True,
) -> LangSmithSettings:

    settings = get_langsmith_settings()

    if require_tracing and not settings.tracing_enabled:
        raise RuntimeError(
            "LANGSMITH_TRACING is not enabled. Set LANGSMITH_TRACING=true."
        )

    if not settings.api_key_configured:
        raise RuntimeError("LANGSMITH_API_KEY is not configured.")

    return settings


# =========================================================
# SAFE DISPLAY
# =========================================================


def safe_settings_summary() -> dict[str, object]:

    settings = get_langsmith_settings()

    return {
        "tracing_enabled": (settings.tracing_enabled),
        "api_key_configured": (settings.api_key_configured),
        "project": (settings.project),
        "endpoint": (settings.endpoint or "default"),
        "workspace_id_configured": (bool(settings.workspace_id)),
    }
