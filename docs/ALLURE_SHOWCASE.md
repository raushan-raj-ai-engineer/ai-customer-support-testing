# Unified AI Quality Showcase

This project keeps two CI concepts separate.

## Fast PR CI

```text
.github/workflows/quality-gate.yml
```

Use it for normal push / PR validation.

## Full AI Showcase

```text
.github/workflows/full-ai-quality-report.yml
```

Use it manually to combine:

```text
Business API
RAG retrieval
LangGraph agent
Security
DeepEval / live LLM
LangSmith
Playwright
Screenshots
```

into one Allure report.

---

## One-Time Local Installation

```bash
source .venv/bin/activate

pip install allure-pytest==2.16.0

npm install -D   allure@3.16.0   allure-playwright@3.11.0
```

Commit the package changes:

```bash
git add package.json package-lock.json
git commit -m "add unified Allure AI quality reporting"
```

---

## Local Full Showcase

```bash
chmod +x scripts/run_full_ai_showcase.sh

RUN_LANGSMITH=1 ./scripts/run_full_ai_showcase.sh
```

Open:

```bash
npx allure open allure-report
```

---

## Optional Rich DeepEval Metric Attachments

Existing pytest stdout/stderr is already captured by Allure Pytest.

For a richer metric attachment:

```python
from tests.utils.allure_ai import attach_ai_metric
```

After DeepEval metric execution:

```python
attach_ai_metric(
    metric_name="Faithfulness",
    score=metric.score,
    threshold=metric.threshold,
    passed=metric.score >= metric.threshold,
    reason=getattr(metric, "reason", None),
    evaluator_model="qwen3:4b-instruct",
)
```

This does not change the assertion or threshold.

---

## Self-Hosted Runner

The full workflow uses:

```yaml
runs-on: self-hosted
```

because Ollama models are already available on the development machine.

GitHub:

```text
Repository
→ Settings
→ Actions
→ Runners
→ New self-hosted runner
```

Follow GitHub's commands for your Mac.

When it shows:

```text
Idle
```

run:

```text
Actions
→ Full AI Quality Showcase
→ Run workflow
```

---

## LangSmith Secret

Create:

```text
LANGSMITH_API_KEY
```

under:

```text
Repository
→ Settings
→ Secrets and variables
→ Actions
```

---

## Artifacts

The workflow uploads:

```text
AI-QUALITY-ALLURE-REPORT
AI-QUALITY-RAW-RESULTS
PLAYWRIGHT-EVIDENCE
AI-QUALITY-LOGS
```

Keep the original fast `quality-gate.yml` unchanged.
