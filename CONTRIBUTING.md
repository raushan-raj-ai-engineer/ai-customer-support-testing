# Contributing Guide

Thank you for contributing.

This project is intentionally designed as an AI testing learning repository, so changes should remain:

```text
clear
testable
secure
beginner-readable
```

---

# 1. Before You Change Code

Read:

```text
README.md
AI_SDET_PROJECT_PLAYBOOK.md
docs/ARCHITECTURE.md
docs/TESTING_STRATEGY.md
```

For a new feature:

```text
docs/ADD_NEW_FEATURE.md
```

---

# 2. Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

npm install
npx playwright install chromium

ollama pull llama3.2
ollama pull qwen3:4b-instruct

python -m scripts.build_vector_db
```

---

# 3. Branch Naming

Examples:

```text
feature/cancellation-policy
fix/order-router
test/security-regression
docs/rag-guide
```

---

# 4. Keep Responsibilities Separate

Do not place:

```text
business logic
retrieval
security
tool authorization
HTTP routing
```

all in one file.

Prefer existing layers.

---

# 5. Deterministic First

If exact truth exists, test it with normal code.

Examples:

```text
tool name
policy ID
order ID
HTTP status
task completion
```

Do not use an LLM judge for exact equality.

---

# 6. RAG Changes

If changing:

```text
documents
chunking
embedding model
metadata
vector store
retrieval logic
```

you must:

```text
rebuild Chroma
run RAG tests
review golden dataset
review DeepEval results
```

---

# 7. Agent Changes

If changing router/workflow:

```text
run router tests
run workflow tests
inspect trajectory
run LangSmith experiment
```

New tools must also update security policy.

---

# 8. Security Changes

Never weaken:

```text
tool allowlist
argument validation
write approval
known attack blocking
```

just to make tests pass.

Security gate target stays:

```text
100%
```

---

# 9. UI Changes

Prefer accessible HTML and semantic Playwright locators.

Preferred:

```typescript
getByRole(...)
getByLabel(...)
```

Use IDs when validating a specific unique status/field and semantic alternatives would be ambiguous.

Avoid fixed waits.

---

# 10. Test Commands

Deterministic Python:

```bash
pytest -v   -m "not live_llm and not deepeval and not live_agent and not live_langsmith"
```

Security:

```bash
pytest tests/security -v
python -m scripts.run_security_gate
```

TypeScript:

```bash
npx tsc --noEmit
```

Playwright:

```bash
npm run test:e2e
```

Release:

```bash
./scripts/release_gate.sh
```

---

# 11. Pull Request Checklist

```text
[ ] change has one clear purpose
[ ] deterministic tests added/updated
[ ] golden dataset updated when required
[ ] no threshold weakened without justification
[ ] no secret committed
[ ] no write tool added without approval policy
[ ] security tests pass
[ ] TypeScript compiles
[ ] Playwright passes
[ ] release gate passes
[ ] docs updated when architecture changes
```

---

# 12. Commit Messages

Good:

```text
fix router handling for unknown orders
add cancellation policy retrieval tests
enforce approval for ticket write
document RAG evaluation workflow
```

Avoid:

```text
changes
fix
update stuff
```

---

# 13. Do Not Commit

```text
.env
API keys
tokens
.venv/
node_modules/
chroma_db/
playwright-report/
test-results/
```

---

# 14. Documentation Rule

If you introduce a new concept a beginner cannot infer from existing docs, update:

```text
README
Playbook
or relevant docs/*
```

The repository should remain learnable, not only runnable.
