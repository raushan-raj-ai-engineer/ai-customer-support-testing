from __future__ import annotations

import os
from functools import lru_cache

from deepeval.models import (
    OllamaModel,
)

DEFAULT_OLLAMA_URL = "http://localhost:11434"


DEFAULT_EVALUATION_MODEL = "qwen3:4b-instruct"


@lru_cache(maxsize=1)
def get_evaluation_model() -> OllamaModel:
    """
    DeepEval LLM-as-a-Judge.

    Important:

    Application model:
        llama3.2

    Evaluation model:
        qwen3:4b-instruct

    Keeping them separate reduces self-evaluation bias
    and gives us a more instruction-capable judge.

    Environment override:

        DEEPEVAL_OLLAMA_MODEL=gemma3:4b
    """

    model_name = os.getenv(
        "DEEPEVAL_OLLAMA_MODEL",
        DEFAULT_EVALUATION_MODEL,
    )

    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        DEFAULT_OLLAMA_URL,
    )

    return OllamaModel(
        model=model_name,
        base_url=base_url,
        temperature=0,
    )
