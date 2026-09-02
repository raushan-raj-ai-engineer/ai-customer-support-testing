from __future__ import annotations

import re
from dataclasses import dataclass

from app.security.models import (
    SecurityFinding,
)

# =========================================================
# RESULT MODEL
# =========================================================


@dataclass(frozen=True)
class RedactionResult:
    text: str

    findings: list[SecurityFinding]


# =========================================================
# PATTERNS
# =========================================================


EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)


BEARER_TOKEN_PATTERN = re.compile(
    r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}",
    re.IGNORECASE,
)


API_KEY_PATTERN = re.compile(
    r"\b(?:sk|lsv2)[-_][A-Za-z0-9_-]{16,}\b",
    re.IGNORECASE,
)


NAMED_SECRET_PATTERN = re.compile(
    r"""
    \b
    (?:
        api[_\-\s]?key
        |
        access[_\-\s]?token
        |
        secret[_\-\s]?key
        |
        auth[_\-\s]?token
    )
    \s*
    (?:
        :
        |
        =
    )
    \s*
    ["']?
    [A-Za-z0-9._~+/=-]{8,}
    ["']?
    """,
    re.IGNORECASE | re.VERBOSE,
)


PHONE_CANDIDATE_PATTERN = re.compile(
    r"""
    (?<!\d)
    \+?
    \d
    [\d\s().-]{8,}
    \d
    (?!\d)
    """,
    re.VERBOSE,
)


CARD_CANDIDATE_PATTERN = re.compile(
    r"""
    (?<!\d)
    (?:
        \d[\s-]*
    ){13,19}
    (?!\d)
    """,
    re.VERBOSE,
)


# =========================================================
# LUHN CHECK
# =========================================================


def _luhn_valid(
    number: str,
) -> bool:

    digits = [int(char) for char in number if char.isdigit()]

    if not (13 <= len(digits) <= 19):
        return False

    checksum = 0

    parity = len(digits) % 2

    for index, digit in enumerate(digits):
        value = digit

        if index % 2 == parity:
            value *= 2

            if value > 9:
                value -= 9

        checksum += value

    return checksum % 10 == 0


# =========================================================
# GENERIC REPLACE
# =========================================================


def _replace_pattern(
    text: str,
    pattern: re.Pattern[str],
    replacement: str,
) -> tuple[str, int]:

    updated, count = pattern.subn(
        replacement,
        text,
    )

    return (
        updated,
        count,
    )


# =========================================================
# PHONE REDACTION
# =========================================================


def _redact_phone_numbers(
    text: str,
) -> tuple[str, int]:

    count = 0

    def replace(
        match: re.Match[str],
    ) -> str:

        nonlocal count

        candidate = match.group(0)

        digits = "".join(character for character in candidate if character.isdigit())

        if not (10 <= len(digits) <= 15):
            return candidate

        count += 1

        return "[REDACTED_PHONE]"

    updated = PHONE_CANDIDATE_PATTERN.sub(
        replace,
        text,
    )

    return (
        updated,
        count,
    )


# =========================================================
# CARD REDACTION
# =========================================================


def _redact_cards(
    text: str,
) -> tuple[str, int]:

    count = 0

    def replace(
        match: re.Match[str],
    ) -> str:

        nonlocal count

        candidate = match.group(0)

        if not (_luhn_valid(candidate)):
            return candidate

        count += 1

        return "[REDACTED_PAYMENT_CARD]"

    updated = CARD_CANDIDATE_PATTERN.sub(
        replace,
        text,
    )

    return (
        updated,
        count,
    )


# =========================================================
# MAIN PUBLIC FUNCTION
# =========================================================


def redact_sensitive_text(
    text: str,
) -> RedactionResult:
    """
    Redact potentially sensitive information before
    sending data to the AI model or returning it to users.

    This function is intentionally deterministic.
    """

    sanitized = text

    findings: list[SecurityFinding] = []

    # -----------------------------------------------------
    # API KEYS
    # -----------------------------------------------------

    sanitized, count = _replace_pattern(
        sanitized,
        API_KEY_PATTERN,
        "[REDACTED_SECRET]",
    )

    if count > 0:
        findings.append(
            SecurityFinding(
                rule_id=("SEC-DATA-001"),
                category=("sensitive_data"),
                severity="high",
                message=("Credential-like secret was redacted."),
            )
        )

    # -----------------------------------------------------
    # NAMED SECRETS
    # -----------------------------------------------------

    sanitized, count = _replace_pattern(
        sanitized,
        NAMED_SECRET_PATTERN,
        "[REDACTED_SECRET]",
    )

    if count > 0:
        findings.append(
            SecurityFinding(
                rule_id=("SEC-DATA-002"),
                category=("sensitive_data"),
                severity="high",
                message=("Named credential was redacted."),
            )
        )

    # -----------------------------------------------------
    # BEARER TOKEN
    # -----------------------------------------------------

    sanitized, count = _replace_pattern(
        sanitized,
        BEARER_TOKEN_PATTERN,
        "[REDACTED_BEARER_TOKEN]",
    )

    if count > 0:
        findings.append(
            SecurityFinding(
                rule_id=("SEC-DATA-003"),
                category=("sensitive_data"),
                severity="high",
                message=("Bearer token was redacted."),
            )
        )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    sanitized, count = _replace_pattern(
        sanitized,
        EMAIL_PATTERN,
        "[REDACTED_EMAIL]",
    )

    if count > 0:
        findings.append(
            SecurityFinding(
                rule_id=("SEC-DATA-004"),
                category=("sensitive_data"),
                severity="medium",
                message=("Email address was redacted."),
            )
        )

    # -----------------------------------------------------
    # PAYMENT CARD
    # -----------------------------------------------------

    sanitized, count = _redact_cards(sanitized)

    if count > 0:
        findings.append(
            SecurityFinding(
                rule_id=("SEC-DATA-005"),
                category=("sensitive_data"),
                severity="critical",
                message=("Payment-card data was redacted."),
            )
        )

    # -----------------------------------------------------
    # PHONE
    # -----------------------------------------------------

    sanitized, count = _redact_phone_numbers(sanitized)

    if count > 0:
        findings.append(
            SecurityFinding(
                rule_id=("SEC-DATA-006"),
                category=("sensitive_data"),
                severity="medium",
                message=("Phone number was redacted."),
            )
        )

    return RedactionResult(
        text=(sanitized),
        findings=(findings),
    )
