# Start Here — AI Customer Support Testing Platform

This file gives a beginner the **recommended reading order** for the repository.

Do not open random files and try to understand everything at once.

---

## 1. First Read

Start with:

```text
README.md
```

You will learn:

- what the project does,
- architecture,
- setup,
- commands,
- project stages,
- how to run tests.

---

## 2. Then Read the Engineering Playbook

Next:

```text
AI_SDET_PROJECT_PLAYBOOK.md
```

This explains:

- why each major file exists,
- how the code flows,
- important functions/classes,
- test responsibilities,
- real bugs found,
- design benefits,
- interview explanations.

---

## 3. Architecture

Read:

```text
docs/ARCHITECTURE.md
```

Use it to understand:

```text
UI
→ API
→ Security
→ Router
→ LangGraph
→ Tools
→ RAG
→ Output Guard
→ Evaluation
```

---

## 4. Testing Strategy

Read:

```text
docs/TESTING_STRATEGY.md
```

This answers:

```text
Which test belongs where?
When should I use pytest?
When should I use DeepEval?
When should I use LangSmith?
When should I use Playwright?
When should I use MCP?
What should block a release?
```

---

## 5. Security

Read:

```text
SECURITY.md
```

This explains:

- prompt injection,
- secret leakage,
- PII redaction,
- least privilege,
- tool authorization,
- HITL approval,
- security quality gate.

---

## 6. Learn How to Extend the Project

Read:

```text
docs/ADD_NEW_FEATURE.md
```

It walks through adding a new capability safely.

Example:

```text
Cancellation Policy
```

and shows which files/tests must change.

---

## 7. Interview Preparation

Read:

```text
docs/INTERVIEW_GUIDE.md
```

This contains:

- project pitch,
- architecture questions,
- RAG questions,
- agent questions,
- DeepEval questions,
- LangSmith questions,
- security questions,
- Playwright/MCP questions,
- CI/CD questions.

---

## 8. Contributing

Read:

```text
CONTRIBUTING.md
```

before changing:

- business rules,
- policies,
- RAG,
- agent tools,
- security controls,
- browser tests,
- datasets.

---

# Recommended Hands-On Order

```text
Day 1:
FastAPI + pytest

Day 2:
Policy docs + chunking

Day 3:
Embeddings + Chroma

Day 4:
RAG + retrieval tests

Day 5:
DeepEval

Day 6:
LangGraph router + agent

Day 7:
LangSmith

Day 8:
Security + HITL

Day 9:
Playwright

Day 10:
MCP + CI/CD + release gate
```

---

# One Rule to Remember

For every layer ask:

```text
What can fail here?
How do I observe the failure?
Can I test it deterministically?
If not, what semantic metric should I use?
Should this failure block release?
```

That mindset is more important than memorizing framework syntax.
