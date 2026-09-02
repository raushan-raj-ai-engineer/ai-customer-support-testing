from __future__ import annotations

from langsmith import (
    Client,
)

from app.observability.config import (
    safe_settings_summary,
    validate_langsmith_settings,
)
from app.observability.dataset import (
    LANGSMITH_DATASET_NAME,
)


def main() -> None:

    print()
    print("=" * 70)

    print("LANGSMITH CONNECTION CHECK")

    print("=" * 70)

    settings = safe_settings_summary()

    for (
        key,
        value,
    ) in settings.items():
        print(f"{key}: {value}")

    print()

    validate_langsmith_settings()

    client = Client()

    # Harmless authenticated read request.
    dataset_exists = client.has_dataset(dataset_name=(LANGSMITH_DATASET_NAME))

    print("LangSmith connection: OK")

    print(f"Agent dataset exists: {dataset_exists}")

    print("=" * 70)


if __name__ == "__main__":
    main()
