from __future__ import annotations

from pathlib import Path

import allure
import pytest


PROJECT_EPIC = "AI Customer Support Quality Platform"


def _has_marker(
    request: pytest.FixtureRequest,
    marker_name: str,
) -> bool:
    return (
        request.node.get_closest_marker(
            marker_name,
        )
        is not None
    )


def _feature_from_test(
    request: pytest.FixtureRequest,
) -> tuple[str, str]:

    if (
        _has_marker(request, "deepeval")
        or _has_marker(request, "live_llm")
    ):
        return (
            "LLM / DeepEval",
            "Semantic AI Quality",
        )

    if _has_marker(
        request,
        "live_langsmith",
    ):
        return (
            "LangSmith Live",
            "Observability",
        )

    if _has_marker(
        request,
        "live_agent",
    ):
        return (
            "Live LangGraph Agent",
            "Agent Quality",
        )

    path = Path(
        str(request.node.path)
    )

    normalized = (
        "/"
        + str(path).replace("\\", "/")
    )

    if "/tests/rag/" in normalized:
        return (
            "RAG & Retrieval",
            "AI Quality",
        )

    if "/tests/agent/" in normalized:
        return (
            "LangGraph Agent",
            "Agent Quality",
        )

    if "/tests/security/" in normalized:
        return (
            "AI Security",
            "Security Quality",
        )

    if "/tests/observability/" in normalized:
        return (
            "LangSmith / Observability",
            "Observability",
        )

    if "/tests/evaluation/" in normalized:
        return (
            "Evaluation Dataset",
            "Semantic AI Quality",
        )

    if path.name in {
        "test_health.py",
        "test_orders.py",
        "test_policies.py",
        "test_tickets.py",
    }:
        return (
            "Business APIs",
            "Deterministic Quality",
        )

    return (
        "Python Regression",
        "Deterministic Quality",
    )


@pytest.fixture(
    autouse=True,
)
def allure_quality_labels(
    request: pytest.FixtureRequest,
):

    feature, parent_suite = (
        _feature_from_test(request)
    )

    allure.dynamic.epic(
        PROJECT_EPIC,
    )

    allure.dynamic.parent_suite(
        parent_suite,
    )

    allure.dynamic.feature(
        feature,
    )

    allure.dynamic.suite(
        request.node.path.parent.name
        or "tests",
    )

    allure.dynamic.sub_suite(
        request.node.path.name,
    )

    marker_names = {
        marker.name
        for marker
        in request.node.iter_markers()
    }

    if "deepeval" in marker_names:
        allure.dynamic.tag(
            "deepeval",
            "llm-evaluation",
        )

    if "live_llm" in marker_names:
        allure.dynamic.tag(
            "live-llm",
        )

    if "live_agent" in marker_names:
        allure.dynamic.tag(
            "live-agent",
        )

    if "live_langsmith" in marker_names:
        allure.dynamic.tag(
            "langsmith",
            "live-observability",
        )

    if "security" in marker_names:
        allure.dynamic.tag(
            "security",
        )

    yield
