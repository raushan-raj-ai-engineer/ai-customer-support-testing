from __future__ import annotations

import sys

from app.rag.vector_store import (
    PolicyVectorStore,
)


def main() -> None:

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])

    else:
        query = "Can I return my laptop after 20 days?"

    store = PolicyVectorStore()

    print()
    print(f"QUERY: {query}")
    print()

    hits = store.search(
        query=query,
        n_results=3,
    )

    if not hits:
        print("No results found.")

        return

    for rank, hit in enumerate(
        hits,
        start=1,
    ):
        print(f"RESULT #{rank}")

        print(f"Policy: {hit.policy_id}")

        print(f"Chunk: {hit.chunk_id}")

        print(f"Distance: {hit.distance:.4f}")

        print("Content:")

        print(hit.content)

        print("-" * 70)


if __name__ == "__main__":
    main()
