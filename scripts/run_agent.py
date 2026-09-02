from __future__ import annotations

import sys

from app.agent.workflow import (
    SupportAgent,
)


def main() -> None:

    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])

    else:
        message = "How long does standard shipping take?"

    agent = SupportAgent()

    result = agent.run(message)

    print()
    print("=" * 70)

    print("LANGGRAPH CUSTOMER SUPPORT AGENT")

    print("=" * 70)

    print(f"Customer:\n{message}")

    print()

    print(f"Intent: {result.intent}")

    print()

    print("Trajectory:")

    for step in result.trajectory:
        print(f"  → {step}")

    print()

    print("Tool Calls:")

    if not result.tool_calls:
        print("  none")

    for call in result.tool_calls:
        print(f"  - {call.name}")

        print(f"    success={call.success}")

    print()

    print(f"Task completed: {result.task_completed}")

    if result.error:
        print(f"Error: {result.error}")

    print()

    print("Agent Answer:")

    print(result.answer)

    print("=" * 70)


if __name__ == "__main__":
    main()
