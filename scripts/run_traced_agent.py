from __future__ import annotations

import json
import sys

from langchain_core.tracers.langchain import (
    wait_for_all_tracers,
)

from app.observability.config import (
    validate_langsmith_settings,
)
from app.observability.tracing import (
    run_traced_agent,
)


def main() -> None:

    validate_langsmith_settings()

    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])

    else:
        message = "How long does standard shipping take?"

    try:
        result = run_traced_agent(message)

        print()
        print("=" * 70)

        print("TRACED LANGGRAPH AGENT")

        print("=" * 70)

        print(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )

        print("=" * 70)

    finally:
        # LangChain tracing normally sends data
        # in background. Ensure it is sent before
        # this short CLI process exits.
        wait_for_all_tracers()


if __name__ == "__main__":
    main()
