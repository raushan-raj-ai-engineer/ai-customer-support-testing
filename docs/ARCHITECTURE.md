# Architecture Guide

## 1. Goal

The project is a production-style learning system for testing an AI customer-support application.

The main engineering goal is not just:

```text
Can the chatbot answer?
```

It is:

```text
Can we prove the system is
correct,
grounded,
observable,
secure,
testable,
and safe to release?
```

---

# 2. Complete Runtime Flow

```text
Customer
   ↓
Support UI
   ↓
FastAPI
   ↓
SecureSupportAgent
   ↓
InputGuard
   ↓
SupportIntentRouter
   ↓
LangGraph SupportAgent
   ↓
ToolPolicy
   ↓
┌───────────────────────────────┐
│ RAG Policy Lookup             │
│ Order Lookup                  │
│ Ticket Creation               │
└───────────────────────────────┘
   ↓
OutputGuard
   ↓
Secure Response
```

---

# 3. Quality Flow

```text
Source Code
   ↓
Unit / API Tests
   ↓
RAG Retrieval Tests
   ↓
Agent Tests
   ↓
Security Tests
   ↓
Playwright E2E
   ↓
DeepEval Semantic Evaluation
   ↓
LangSmith Experiments
   ↓
Release Gate
```

---

# 4. FastAPI Layer

Responsibilities:

- API contracts,
- request validation,
- response validation,
- deterministic business endpoints,
- secure-agent endpoint,
- support UI hosting.

Important files:

```text
app/main.py
app/routes.py
app/models.py
app/ui.py
```

Design rule:

> Routes should coordinate services, not contain all business/AI logic.

---

# 5. Business Layer

Important files:

```text
app/data.py
app/knowledge.py
app/services/order_service.py
app/services/ticket_service.py
```

Why this layer exists:

The AI agent should reuse deterministic application capabilities instead of duplicating business rules inside prompts.

Example:

```text
Agent
  ↓
order_lookup tool
  ↓
order service
```

rather than:

```text
LLM guesses order state
```

---

# 6. RAG Architecture

```text
Policy Markdown
   ↓
Document Loader
   ↓
Sentence-Aware Chunker
   ↓
SentenceTransformer
   ↓
Embeddings
   ↓
ChromaDB
   ↓
Semantic Retrieval
   ↓
Focused Policy Retrieval
   ↓
LangChain Prompt
   ↓
Ollama llama3.2
   ↓
Grounded Answer
```

## Why sentence-aware chunks?

Bad:

```text
Customers receive a tracking
```

Good:

```text
Customers receive a tracking number after the order is shipped.
```

A complete fact is better evidence.

---

# 7. Two-Pass Retrieval

The RAG system uses a two-stage idea:

```text
Question
   ↓
Broad candidate search
   ↓
Best policy domain
   ↓
Metadata-filtered search
   ↓
Final context
```

Benefit:

- reduces irrelevant policy mixing,
- improves grounded context,
- makes retrieval easier to debug.

---

# 8. Agent Architecture

Supported intents:

```text
policy
order
ticket
order_policy
unsupported
```

Graph:

```text
START
  ↓
route
  ├── policy        → rag_tool ─────────┐
  ├── order         → order_tool ───────┤
  ├── ticket        → ticket_tool ──────┤
  ├── order_policy  → order_tool        │
  │                    ↓                │
  │                  rag_tool ──────────┤
  └── unsupported   → finalize          │
                                        ↓
                                      END
```

---

# 9. Hybrid Routing

The router uses deterministic rules for high-confidence business patterns.

Example:

```text
Where is ORD-9999?
```

does not need an LLM to determine that it is an order request.

Benefits:

```text
lower latency
lower cost
less nondeterminism
easier testing
```

LLM routing remains useful for ambiguous natural language.

---

# 10. Query Decomposition

Customer:

```text
Can I return ORD-1001?
```

This is decomposed.

Order domain:

```text
ORD-1001
→ order_lookup
```

Policy domain:

```text
return window
→ RAG
```

This prevents the order ID from polluting policy retrieval.

---

# 11. Security Architecture

```text
Raw Input
   ↓
InputGuard
   ├── prompt injection
   ├── prompt leakage
   ├── tool manipulation
   ├── secret extraction
   └── sensitive-data redaction
   ↓
Approved/Sanitized Input
   ↓
Route
   ↓
ToolPolicy
   ├── tool allowlist
   ├── exact sequence
   ├── argument validation
   └── write approval
   ↓
Tool Execution
   ↓
OutputGuard
   ├── secret leakage
   ├── prompt leakage
   └── PII redaction
   ↓
User
```

Critical principle:

> The LLM does not decide its own permissions.

---

# 12. Human-in-the-Loop

Reads:

```text
order_lookup
rag_policy_lookup
```

can execute without write approval.

Writes:

```text
ticket_create
```

require explicit approval.

This limits excessive agency.

---

# 13. Observability Architecture

LangSmith captures:

```text
top-level agent request
router behavior
tool calls
tool inputs
tool output
final output
experiment scores
```

Evaluation dataset compares expected vs actual:

```text
intent
tool sequence
task completion
required facts
approved tools
```

---

# 14. Browser Architecture

Normal Playwright tests:

```text
Static Support UI
   ↓
Mock Secure API
   ↓
Deterministic Browser Assertions
```

Why mock?

To test UI independently of model runtime.

Live E2E:

```text
Playwright
   ↓
Real FastAPI
   ↓
Real Secure Agent
   ↓
Real Business Tool
```

This is optional because it is slower and more environment-dependent.

---

# 15. CI/CD Architecture

PR quality gate:

```text
Python deterministic tests
   ↓
Security hard gate
   ↓
TypeScript compiler
   ↓
Playwright deterministic E2E
   ↓
PASS / FAIL
```

Live semantic/cloud checks are separate:

```text
DeepEval
LangSmith
MCP
live backend AI
```

---

# 16. Data Boundaries

The system deliberately separates:

```text
Business data
Policy knowledge
Agent state
Security state
Evaluation datasets
Browser test fixtures
```

This reduces coupling.

---

# 17. Main Architectural Benefits

## Reliability

Critical business and security decisions are deterministic.

## Explainability

Tool calls and trajectories are recorded.

## Testability

Each layer can be tested independently.

## Security

Permissions exist outside the model.

## Maintainability

Adding one capability has defined extension points.

## CI Stability

Normal PR tests do not depend on a live LLM.

---

# 18. Architectural Anti-Patterns Avoided

The project avoids:

```text
one giant prompt controlling everything
LLM deciding tool permissions
LLM judge for exact facts
UI tests requiring live model every run
blind raw multi-domain queries sent to every tool
write tools executing without approval
security implemented only in system prompt
```

---

# 19. Architecture Review Checklist

Before changing the system:

```text
[ ] Which layer owns this responsibility?
[ ] Is business logic being duplicated?
[ ] Is exact logic deterministic?
[ ] Does this introduce a new tool?
[ ] Does ToolPolicy need updating?
[ ] Does the security model change?
[ ] Does the RAG dataset change?
[ ] Does the LangSmith dataset change?
[ ] Do browser tests need a new state?
[ ] Does release gate still pass?
```
