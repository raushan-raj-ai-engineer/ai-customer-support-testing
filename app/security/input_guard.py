from __future__ import annotations

import re

from app.security.models import (
    InputGuardResult,
    SecurityFinding,
)
from app.security.redaction import (
    redact_sensitive_text,
)

# =========================================================
# CONFIG
# =========================================================


MAX_INPUT_LENGTH = 2000


# =========================================================
# PROMPT INJECTION PATTERNS
# =========================================================


PROMPT_INJECTION_PATTERNS = [
    re.compile(
        r"""
        ignore
        \s+
        (?:
            all
            |
            any
            |
            the
            |
            previous
            |
            prior
            |
            above
        )?
        \s*
        instructions?
        """,
        re.IGNORECASE | re.VERBOSE,
    ),
    re.compile(
        r"""
        (?:
            bypass
            |
            disable
            |
            override
            |
            remove
        )
        .{0,40}
        (?:
            guardrails?
            |
            safety
            |
            restrictions?
            |
            security
            |
            policy
        )
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    ),
    re.compile(
        r"""
        (?:
            you\s+are\s+now
            |
            enter
        )
        .{0,30}
        (?:
            DAN
            |
            developer\s+mode
            |
            unrestricted\s+mode
            |
            jailbreak
        )
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    ),
    re.compile(
        r"""
        (?:
            act
            |
            pretend
        )
        .{0,30}
        (?:
            system
            |
            developer
            |
            root
            |
            administrator
        )
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    ),
    re.compile(
        r"""
        <\|
        (?:
            system
            |
            developer
        )
        \|>
        """,
        re.IGNORECASE | re.VERBOSE,
    ),
]


# =========================================================
# PROMPT LEAKAGE PATTERNS
# =========================================================


PROMPT_LEAK_PATTERNS = [
    re.compile(
        r"""
        (?:
            reveal
            |
            show
            |
            print
            |
            dump
            |
            expose
            |
            repeat
        )
        .{0,50}
        (?:
            system\s+prompt
            |
            developer\s+prompt
            |
            developer\s+message
            |
            hidden\s+instructions?
            |
            internal\s+instructions?
        )
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    ),
    re.compile(
        r"""
        what
        \s+
        (?:are|is)
        \s+
        your
        .{0,20}
        (?:
            system\s+instructions?
            |
            hidden\s+instructions?
        )
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    ),
]


# =========================================================
# TOOL MANIPULATION
# =========================================================


TOOL_MANIPULATION_PATTERNS = [
    re.compile(
        r"""
        (?:
            call
            |
            invoke
            |
            execute
            |
            run
            |
            use
        )
        .{0,40}
        (?:
            delete_customer
            |
            delete_account
            |
            shell
            |
            terminal
            |
            execute_sql
            |
            database_admin
            |
            filesystem
            |
            admin_tool
        )
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    ),
    re.compile(
        r"""
        (?:
            override
            |
            modify
            |
            change
        )
        .{0,40}
        (?:
            tool\s+arguments?
            |
            function\s+arguments?
            |
            tool\s+permissions?
        )
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    ),
]


# =========================================================
# SECRET EXTRACTION
# =========================================================


SECRET_EXTRACTION_PATTERNS = [
    re.compile(
        r"""
        (?:
            reveal
            |
            show
            |
            print
            |
            dump
            |
            give
            |
            expose
        )
        .{0,50}
        (?:
            api\s*key
            |
            access\s*token
            |
            secret\s*key
            |
            database\s+password
            |
            environment\s+variables?
            |
            LANGSMITH_API_KEY
            |
            OPENAI_API_KEY
        )
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    ),
]


# =========================================================
# HELPER
# =========================================================


def _matches_any(
    text: str,
    patterns: list[re.Pattern[str]],
) -> bool:

    return any(pattern.search(text) is not None for pattern in patterns)


# =========================================================
# INPUT GUARD
# =========================================================


class InputGuard:
    def inspect(
        self,
        message: str,
    ) -> InputGuardResult:

        original = message.strip()

        findings: list[SecurityFinding] = []

        # -------------------------------------------------
        # EMPTY
        # -------------------------------------------------

        if not original:
            findings.append(
                SecurityFinding(
                    rule_id=("SEC-INPUT-001"),
                    category=("input_limits"),
                    severity="medium",
                    message=("Empty customer input is not allowed."),
                )
            )

            return InputGuardResult(
                allowed=False,
                sanitized_input="",
                findings=findings,
            )

        # -------------------------------------------------
        # LENGTH
        # -------------------------------------------------

        if len(original) > MAX_INPUT_LENGTH:
            findings.append(
                SecurityFinding(
                    rule_id=("SEC-INPUT-002"),
                    category=("input_limits"),
                    severity="high",
                    message=("Input exceeds the security length limit."),
                )
            )

            return InputGuardResult(
                allowed=False,
                sanitized_input="",
                findings=findings,
            )

        # -------------------------------------------------
        # PROMPT INJECTION
        # -------------------------------------------------

        if _matches_any(
            original,
            PROMPT_INJECTION_PATTERNS,
        ):
            findings.append(
                SecurityFinding(
                    rule_id=("SEC-INJECT-001"),
                    category=("prompt_injection"),
                    severity="critical",
                    message=("Prompt-injection attempt was detected."),
                )
            )

        # -------------------------------------------------
        # PROMPT LEAKAGE
        # -------------------------------------------------

        if _matches_any(
            original,
            PROMPT_LEAK_PATTERNS,
        ):
            findings.append(
                SecurityFinding(
                    rule_id=("SEC-PROMPT-001"),
                    category=("prompt_leakage"),
                    severity="high",
                    message=(
                        "Attempt to obtain internal prompt instructions detected."
                    ),
                )
            )

        # -------------------------------------------------
        # TOOL MANIPULATION
        # -------------------------------------------------

        if _matches_any(
            original,
            TOOL_MANIPULATION_PATTERNS,
        ):
            findings.append(
                SecurityFinding(
                    rule_id=("SEC-TOOL-001"),
                    category=("tool_manipulation"),
                    severity="critical",
                    message=("Attempt to manipulate agent tools detected."),
                )
            )

        # -------------------------------------------------
        # SECRET EXTRACTION
        # -------------------------------------------------

        if _matches_any(
            original,
            SECRET_EXTRACTION_PATTERNS,
        ):
            findings.append(
                SecurityFinding(
                    rule_id=("SEC-SECRET-001"),
                    category=("secret_exfiltration"),
                    severity="critical",
                    message=("Attempt to extract credentials or secrets was detected."),
                )
            )

        # -------------------------------------------------
        # HARD BLOCK
        # -------------------------------------------------

        blocking_categories = {
            "prompt_injection",
            "prompt_leakage",
            "tool_manipulation",
            "secret_exfiltration",
        }

        if any(finding.category in blocking_categories for finding in findings):
            return InputGuardResult(
                allowed=False,
                # Do not forward malicious input.
                sanitized_input="",
                findings=findings,
            )

        # -------------------------------------------------
        # PII / SECRET REDACTION
        # -------------------------------------------------

        redaction = redact_sensitive_text(original)

        findings.extend(redaction.findings)

        return InputGuardResult(
            allowed=True,
            sanitized_input=(redaction.text),
            findings=findings,
        )
