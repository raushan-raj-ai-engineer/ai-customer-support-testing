from __future__ import annotations

import json
import sys

from app.security.secure_agent import (
    SecureSupportAgent,
)


def main() -> None:

    arguments = sys.argv[1:]

    approve_write = False

    if "--approve-write" in arguments:
        approve_write = True

        arguments.remove("--approve-write")

    if arguments:
        message = " ".join(arguments)

    else:
        message = "How long does standard shipping take?"

    agent = SecureSupportAgent()

    result = agent.run(
        message,
        approve_write=(approve_write),
    )

    print()
    print("=" * 70)

    print("SECURE AI CUSTOMER SUPPORT AGENT")

    print("=" * 70)

    print(
        json.dumps(
            result.model_dump(),
            indent=2,
            default=str,
        )
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
