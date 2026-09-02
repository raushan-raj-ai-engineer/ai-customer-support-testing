from __future__ import annotations

from app.security.output_guard import (
    OutputGuard,
)


def test_normal_answer_allowed():

    result = OutputGuard().inspect("Standard shipping takes 3 to 5 business days.")

    assert result.allowed is True


def test_email_in_output_redacted():

    result = OutputGuard().inspect("Contact rohit@example.com for more information.")

    assert result.allowed is True

    assert "rohit@example.com" not in result.sanitized_output

    assert "[REDACTED_EMAIL]" in result.sanitized_output


def test_api_key_output_blocked():

    result = OutputGuard().inspect("The key is sk-abcdefghijklmnopqrstuvwxyz1234")

    assert result.allowed is False


def test_environment_secret_output_blocked():

    result = OutputGuard().inspect("LANGSMITH_API_KEY=abc123456789secret")

    assert result.allowed is False


def test_developer_prompt_leak_blocked():

    result = OutputGuard().inspect(
        "BEGIN DEVELOPER MESSAGE developer instructions: do something secret"
    )

    assert result.allowed is False
