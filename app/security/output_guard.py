from __future__ import annotations

import re

from app.security.models import (
    OutputGuardResult,
    SecurityFinding,
)
from app.security.redaction import (
    redact_sensitive_text,
)

# =========================================================
# SAFE FALLBACK
# =========================================================


SECURE_OUTPUT_FALLBACK = (
    "I can't provide internal credentials, secrets, or protected system information."
)


# =========================================================
# LEAK PATTERNS
# =========================================================


OUTPUT_LEAK_PATTERNS = [
    re.compile(
        r"""
        LANGSMITH_API_KEY
        \s*
        =
        """,
        re.IGNORECASE | re.VERBOSE,
    ),
    re.compile(
        r"""
        OPENAI_API_KEY
        \s*
        =
        """,
        re.IGNORECASE | re.VERBOSE,
    ),
    re.compile(
        r"""
        BEGIN
        \s+
        (?:
            SYSTEM
            |
            DEVELOPER
        )
        \s+
        (?:
            PROMPT
            |
            MESSAGE
        )
        """,
        re.IGNORECASE | re.VERBOSE,
    ),
    re.compile(
        r"""
        developer
        \s+
        instructions?
        \s*:
        """,
        re.IGNORECASE | re.VERBOSE,
    ),
]


# =========================================================
# OUTPUT GUARD
# =========================================================


class OutputGuard:
    def inspect(
        self,
        output: str,
    ) -> OutputGuardResult:

        text = output.strip()

        findings: list[SecurityFinding] = []

        leak_detected = any(
            pattern.search(text) is not None for pattern in OUTPUT_LEAK_PATTERNS
        )

        if leak_detected:
            findings.append(
                SecurityFinding(
                    rule_id=("SEC-OUTPUT-001"),
                    category=("output_leakage"),
                    severity="critical",
                    message=(
                        "Potential internal prompt or credential leakage detected."
                    ),
                )
            )

            return OutputGuardResult(
                allowed=False,
                sanitized_output=(SECURE_OUTPUT_FALLBACK),
                findings=findings,
            )

        # -------------------------------------------------
        # REDACT ACCIDENTAL PII / SECRET OUTPUT
        # -------------------------------------------------

        redaction = redact_sensitive_text(text)

        findings.extend(redaction.findings)

        # A credential reaching output is treated
        # more severely than ordinary PII.

        secret_found = any(
            finding.rule_id
            in {
                "SEC-DATA-001",
                "SEC-DATA-002",
                "SEC-DATA-003",
            }
            for finding in redaction.findings
        )

        if secret_found:
            findings.append(
                SecurityFinding(
                    rule_id=("SEC-OUTPUT-002"),
                    category=("output_leakage"),
                    severity="critical",
                    message=("Credential-like content was detected in agent output."),
                )
            )

            return OutputGuardResult(
                allowed=False,
                sanitized_output=(SECURE_OUTPUT_FALLBACK),
                findings=findings,
            )

        return OutputGuardResult(
            allowed=True,
            sanitized_output=(redaction.text),
            findings=findings,
        )
