# AI Testing Strategy

## 1. Goal

This document explains **which test to use, where to use it, why it exists, and what should block a release**.

The most important rule:

> Use deterministic tests for deterministic truth. Use semantic evaluation for semantic quality.

---

# 2. Test Pyramid

```text
                MCP / Human Exploration
                         ▲
                LangSmith Experiments
                         ▲
                DeepEval Semantic Tests
                         ▲
                  Playwright E2E
                         ▲
                  Security Tests
                         ▲
               Agent + RAG Tests
                         ▲
                  API / Unit Tests
```

Lower layers:

```text
fast
cheap
deterministic
frequent
```

Upper layers:

```text
slower
semantic
environment-dependent
less frequent
```

---

# 3. Business API Tests

Use for:

```text
HTTP status
response schema
order data
ticket rules
policy endpoint
validation
```

Examples:

```text
tests/test_health.py
tests/test_orders.py
tests/test_tickets.py
tests/test_policies.py
```

These should run on every PR.

---

# 4. RAG Retrieval Tests

Use for:

```text
chunk correctness
vector DB count
semantic retrieval
top-k behavior
metadata filtering
golden dataset accuracy
```

Files:

```text
tests/rag/test_chunker.py
tests/rag/test_vector_store.py
tests/rag/test_retrieval_quality.py
tests/rag/test_rag_service.py
```

Release impact:

```text
FAIL = block release
```

because these tests are deterministic.

---

# 5. RAG Generation Tests

Use deterministic checks for:

```text
required numbers
required policy IDs
fallback behavior
empty-input behavior
```

Use DeepEval for:

```text
faithfulness
answer relevance
context relevance
business correctness
```

---

# 6. DeepEval Strategy

Metrics:

```text
Faithfulness
Answer Relevancy
Contextual Relevancy
Contextual Precision
Contextual Recall
GEval Business Correctness
```

Example thresholds:

```text
Faithfulness           >= 0.80
Answer Relevancy       >= 0.80
Contextual Relevancy   >= 0.70
Contextual Precision   >= 0.70
Contextual Recall      >= 0.80
Business Correctness   >= 0.80
```

Do not lower thresholds to make failures green.

---

# 7. Evaluator Calibration

Before trusting an evaluator:

```text
known good answer
→ evaluator should pass

known bad answer
→ evaluator should fail
```

The evaluator is also software.

It can be wrong.

---

# 8. Agent Testing

Validate:

```text
intent
tool selection
tool order
tool arguments
trajectory
task completion
final required facts
```

Do not only validate:

```text
final prose
```

Files:

```text
tests/agent/test_router.py
tests/agent/test_agent_workflow.py
```

---

# 9. Task Completion Rule

Tool execution is not task completion.

Example:

```text
order_lookup ran
ORD-9999 not found
```

Therefore:

```text
tool executed = yes
task completed = no
```

Test this explicitly.

---

# 10. Security Testing

Security deterministic checks include:

```text
prompt injection blocked
secret extraction blocked
unauthorized tool blocked
PII redacted
write approval required
argument validation
tool sequence enforcement
output leakage blocked
```

Files:

```text
tests/security/test_input_guard.py
tests/security/test_output_guard.py
tests/security/test_tool_policy.py
tests/security/test_secure_agent.py
tests/security/test_security_dataset.py
```

Security dataset target:

```text
100%
```

Known deterministic attack cases should not be allowed to fail.

---

# 11. LangSmith Testing

LangSmith evaluates behavior across a reusable dataset.

Evaluators:

```text
intent_match
tool_sequence_match
task_completion_match
answer_contains_required_facts
approved_tools_only
```

Use LangSmith for:

```text
offline regression
trace debugging
behavior comparison
experiment history
```

---

# 12. Playwright Strategy

Normal browser suite:

```text
mock secure API
```

Tests:

```text
form
payload
rendering
security badge
tool history
trajectory
approval
```

This keeps browser tests stable.

---

# 13. Live Backend E2E

Run separately.

Use for:

```text
browser → API → secure agent → tool → response
```

Do not make every PR depend on it unless the environment guarantees all dependencies.

---

# 14. MCP Testing

Use MCP for:

```text
exploratory browser testing
goal-driven browser tasks
autonomous scenario validation
```

Do not use MCP as the only regression suite.

---

# 15. CI Test Classification

## Every PR

```text
unit/API
RAG deterministic
agent deterministic
security deterministic
TypeScript compile
Playwright mocked E2E
```

## Local / Dedicated Job

```text
DeepEval
live Ollama
LangSmith
live browser backend
MCP
```

---

# 16. Release Blocking Matrix

| Failure | Block Release? |
|---|---|
| API contract failure | Yes |
| Wrong order data | Yes |
| Retrieval golden dataset failure | Yes |
| Wrong agent tool | Yes |
| Wrong tool sequence | Yes |
| Security known-attack failure | Yes |
| TypeScript compile failure | Yes |
| Playwright deterministic E2E failure | Yes |
| DeepEval threshold failure | Yes for semantic release gate |
| LangSmith cloud unavailable | Depends on release policy |
| HF unauthenticated warning | No |
| Dependency deprecation warning | No, but track it |

---

# 17. How to Diagnose a Failure

## API failure

Run:

```bash
pytest tests/test_orders.py -v
```

## Retrieval failure

Run:

```bash
python -m scripts.query_vector_db
pytest tests/rag/test_vector_store.py -v
```

## RAG answer failure

First prove retrieval.

Then inspect:

```text
prompt
context
model output
DeepEval reason
```

## Agent failure

Run:

```bash
pytest tests/agent/test_router.py -v
pytest tests/agent/test_agent_workflow.py -v
```

Inspect trajectory.

## Security failure

Run:

```bash
pytest tests/security -v
python -m scripts.run_security_gate
```

## UI failure

Run one spec:

```bash
npx playwright test e2e/security-ui.spec.ts
```

Inspect trace/report.

---

# 18. Golden Dataset Rules

Good golden cases should:

```text
have unique IDs
represent real business behavior
contain exact expected facts
avoid ambiguous wording when deterministic
include safe and failing cases
```

Avoid:

```text
changing expected output just because model changed
```

If business truth changes, update dataset intentionally.

---

# 19. Flakiness Prevention

Prefer:

```text
temperature = 0
deterministic routes
mocked browser API
explicit timeouts
no fixed browser sleeps
web-first assertions
stable selectors
separate live tests
```

Avoid:

```text
waitForTimeout
random model selection
unbounded retries
changing thresholds
retrying until green
```

---

# 20. Testing Principle Summary

```text
Business truth  → pytest
Retrieval truth → deterministic RAG tests
Semantic truth  → DeepEval
Agent behavior  → trajectory/tool assertions
Observability   → LangSmith
Security        → deterministic guardrail tests
User behavior   → Playwright
Exploration     → MCP
Release         → combined gate
```
