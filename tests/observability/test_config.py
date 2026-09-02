from __future__ import annotations

from app.observability.config import (
    get_langsmith_settings,
    parse_bool,
    safe_settings_summary,
)


def test_parse_bool_true_values():

    assert parse_bool("true") is True

    assert parse_bool("1") is True

    assert parse_bool("YES") is True


def test_parse_bool_false_values():

    assert parse_bool("false") is False

    assert parse_bool("0") is False

    assert parse_bool(None) is False


def test_settings_read_environment(
    monkeypatch,
):

    monkeypatch.setenv(
        "LANGSMITH_TRACING",
        "true",
    )

    monkeypatch.setenv(
        "LANGSMITH_API_KEY",
        "fake-test-key",
    )

    monkeypatch.setenv(
        "LANGSMITH_PROJECT",
        "test-project",
    )

    settings = get_langsmith_settings()

    assert settings.tracing_enabled is True

    assert settings.api_key_configured is True

    assert settings.project == "test-project"


def test_safe_summary_never_exposes_api_key(
    monkeypatch,
):

    secret = "super-secret-langsmith-key"

    monkeypatch.setenv(
        "LANGSMITH_API_KEY",
        secret,
    )

    summary = safe_settings_summary()

    assert secret not in str(summary)
