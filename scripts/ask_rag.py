from __future__ import annotations

import sys

from app.rag.rag_service import (
    RAGService,
)


def main() -> None:

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])

    else:
        question = "Can I return my laptop after 20 days?"

    print()
    print("=" * 70)

    print("AI CUSTOMER SUPPORT RAG")

    print("=" * 70)

    print(f"Question:\n{question}")

    print()

    service = RAGService()

    response = service.ask(question)

    print("Retrieved Policies:")

    for policy_id in response.retrieved_policy_ids:
        print(f"  - {policy_id}")

    print()

    print("Retrieved Context:")

    for index, context in enumerate(
        response.retrieval_context,
        start=1,
    ):
        print()
        print(f"[Context {index}]")

        print(context)

    print()
    print("-" * 70)

    print("AI Answer:")

    print(response.answer)

    print("=" * 70)


if __name__ == "__main__":
    main()
