from __future__ import annotations

from langchain_core.tracers.langchain import (
    wait_for_all_tracers,
)
from langsmith import (
    Client,
)

from app.observability.config import (
    validate_langsmith_settings,
)
from app.observability.dataset import (
    LANGSMITH_DATASET_NAME,
)
from app.observability.experiment import (
    run_agent_experiment,
)


def main() -> None:

    validate_langsmith_settings()

    client = Client()

    if not client.has_dataset(dataset_name=(LANGSMITH_DATASET_NAME)):
        raise RuntimeError(
            "LangSmith dataset does not exist. "
            "Run:\n\n"
            "python -m "
            "scripts.sync_langsmith_dataset"
        )

    try:
        print()
        print("=" * 70)

        print("RUNNING LANGSMITH AGENT EXPERIMENT")

        print("=" * 70)

        results = run_agent_experiment(client)

        print()
        print("Experiment complete.")

        experiment_name = getattr(
            results,
            "experiment_name",
            None,
        )

        if experiment_name:
            print(f"Experiment name: {experiment_name}")

        print()

        print(results)

        print("=" * 70)

    finally:
        wait_for_all_tracers()


if __name__ == "__main__":
    main()
