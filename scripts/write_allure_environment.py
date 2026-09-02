from __future__ import annotations

import json
import os
import platform
import subprocess
from pathlib import Path


RESULTS_DIR = Path(
    os.environ.get(
        "ALLURE_RESULTS_DIR",
        "allure-results",
    )
)


def command_output(
    *args: str,
) -> str:
    try:
        completed = subprocess.run(
            list(args),
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )

        value = (
            completed.stdout.strip()
            or completed.stderr.strip()
        )

        if not value:
            return "unknown"

        return value.splitlines()[0]

    except Exception:
        return "unavailable"


def write_environment() -> None:
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    properties = {
        "Project":
            "AI Customer Support Testing Platform",

        "Python":
            platform.python_version(),

        "Platform":
            platform.platform(),

        "Node":
            command_output(
                "node",
                "--version",
            ),

        "Playwright":
            command_output(
                "npx",
                "playwright",
                "--version",
            ),

        "Ollama":
            command_output(
                "ollama",
                "--version",
            ),

        "Generator_Model":
            os.environ.get(
                "OLLAMA_APP_MODEL",
                "llama3.2",
            ),

        "Evaluation_Model":
            os.environ.get(
                "OLLAMA_EVALUATION_MODEL",
                "qwen3:4b-instruct",
            ),

        "LangSmith_Project":
            os.environ.get(
                "LANGSMITH_PROJECT",
                "not-configured",
            ),

        "Execution":
            (
                "GitHub Actions"
                if os.environ.get(
                    "GITHUB_ACTIONS",
                )
                == "true"
                else "Local"
            ),
    }

    (
        RESULTS_DIR
        / "environment.properties"
    ).write_text(
        "\n".join(
            f"{key}={value}"
            for key, value
            in properties.items()
        )
        + "\n",
        encoding="utf-8",
    )


def write_executor() -> None:
    if (
        os.environ.get(
            "GITHUB_ACTIONS",
        )
        == "true"
    ):
        server_url = os.environ.get(
            "GITHUB_SERVER_URL",
            "https://github.com",
        )

        repository = os.environ.get(
            "GITHUB_REPOSITORY",
            "",
        )

        run_id = os.environ.get(
            "GITHUB_RUN_ID",
            "",
        )

        executor = {
            "name":
                "GitHub Actions",

            "type":
                "github",

            "buildName":
                os.environ.get(
                    "GITHUB_WORKFLOW",
                    "Full AI Quality Showcase",
                ),

            "buildOrder":
                os.environ.get(
                    "GITHUB_RUN_NUMBER",
                    "0",
                ),

            "buildUrl":
                (
                    f"{server_url}/"
                    f"{repository}/"
                    f"actions/runs/{run_id}"
                ),

            "reportName":
                "AI Customer Support Master Quality Report",
        }
    else:
        executor = {
            "name":
                "Local Machine",

            "type":
                "local",

            "buildName":
                "Local Full AI Quality Showcase",

            "reportName":
                "AI Customer Support Master Quality Report",
        }

    (
        RESULTS_DIR
        / "executor.json"
    ).write_text(
        json.dumps(
            executor,
            indent=2,
        ),
        encoding="utf-8",
    )


def write_categories() -> None:
    categories = [
        {
            "name":
                "AI Security Failure",

            "matchedStatuses": [
                "failed",
                "broken",
            ],

            "messageRegex":
                (
                    ".*("
                    "SEC-|"
                    "prompt injection|"
                    "secret|"
                    "unauthorized tool|"
                    "write approval"
                    ").*"
                ),
        },
        {
            "name":
                "RAG / Retrieval Failure",

            "matchedStatuses": [
                "failed",
                "broken",
            ],

            "messageRegex":
                (
                    ".*("
                    "retriev|"
                    "context|"
                    "policy|"
                    "Chroma|"
                    "vector"
                    ").*"
                ),
        },
        {
            "name":
                "LLM Evaluation Failure",

            "matchedStatuses": [
                "failed",
                "broken",
            ],

            "messageRegex":
                (
                    ".*("
                    "Faithfulness|"
                    "Relevancy|"
                    "Contextual|"
                    "GEval|"
                    "DeepEval"
                    ").*"
                ),
        },
        {
            "name":
                "Agent Workflow Failure",

            "matchedStatuses": [
                "failed",
                "broken",
            ],

            "messageRegex":
                (
                    ".*("
                    "intent|"
                    "tool sequence|"
                    "trajectory|"
                    "task completion"
                    ").*"
                ),
        },
        {
            "name":
                "Playwright UI Failure",

            "matchedStatuses": [
                "failed",
                "broken",
            ],

            "messageRegex":
                (
                    ".*("
                    "locator|"
                    "toBeVisible|"
                    "toHaveText|"
                    "toContainText|"
                    "browserType"
                    ").*"
                ),
        },
    ]

    (
        RESULTS_DIR
        / "categories.json"
    ).write_text(
        json.dumps(
            categories,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    write_environment()
    write_executor()
    write_categories()

    print(
        "Allure metadata written to",
        RESULTS_DIR,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
