from __future__ import annotations

import os

import pytest
from langsmith import (
    Client,
)

from app.observability.config import (
    validate_langsmith_settings,
)

RUN_LIVE_LANGSMITH = (
    os.getenv(
        "RUN_LIVE_LANGSMITH",
        "0",
    )
    == "1"
)


pytestmark = [
    pytest.mark.live_langsmith,
]


@pytest.mark.skipif(
    not RUN_LIVE_LANGSMITH,
    reason=("Set RUN_LIVE_LANGSMITH=1 to run LangSmith connectivity test."),
)
def test_langsmith_connection():

    validate_langsmith_settings()

    client = Client()

    # Safe authenticated read.
    result = client.has_dataset(dataset_name=("ai-customer-support-agent-v1"))

    assert isinstance(
        result,
        bool,
    )
