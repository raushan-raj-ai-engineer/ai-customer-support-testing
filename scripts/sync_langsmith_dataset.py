from __future__ import annotations

from langsmith import (
    Client,
)

from app.observability.config import (
    validate_langsmith_settings,
)
from app.observability.dataset import (
    sync_langsmith_dataset,
)


def main() -> None:

    validate_langsmith_settings(require_tracing=False)

    client = Client()

    result = sync_langsmith_dataset(client)

    print()
    print("=" * 70)

    print("LANGSMITH DATASET")

    print("=" * 70)

    print(result)

    print("=" * 70)


if __name__ == "__main__":
    main()
