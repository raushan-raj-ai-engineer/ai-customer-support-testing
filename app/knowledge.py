from __future__ import annotations

from pathlib import Path

from app.data import POLICIES
from app.models import PolicyResponse

# =========================================================
# KNOWLEDGE BASE PATH
# =========================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base"


# =========================================================
# LOAD POLICY
# =========================================================


def load_policy(
    policy_name: str,
) -> PolicyResponse | None:

    normalized_name = policy_name.strip().lower()

    config = POLICIES.get(normalized_name)

    if config is None:
        return None

    file_path = KNOWLEDGE_BASE / config["filename"]

    if not file_path.exists():
        raise FileNotFoundError(f"Knowledge file missing: {file_path}")

    content = file_path.read_text(encoding="utf-8")

    return PolicyResponse(
        policy_id=(config["policy_id"]),
        title=(config["title"]),
        content=content,
    )
