# Interview Guide — AI Automation / GenAI QA / Agentic AI SDET

This guide is based on the project architecture.

Use the answers as a framework. Do not memorize every word.

---

# 1. 60-Second Project Pitch

> I built a production-style AI customer-support testing platform. FastAPI provides deterministic business APIs. Policy documents are chunked into complete sentences, embedded with Sentence Transformers and stored in ChromaDB. LangChain performs RAG, while a LangGraph agent routes requests between policy retrieval, order lookup and ticket creation. DeepEval provides semantic quality gates and LangSmith provides tracing, datasets and agent experiments. Security is implemented outside the LLM using prompt-injection detection, PII redaction, deterministic tool authorization, argument validation and HITL approval for write operations. Playwright TypeScript validates the browser UI, Playwright MCP supports autonomous browser testing, and a final release gate combines deterministic Python, security, TypeScript and E2E checks.

---

# 2. Why Did You Start With FastAPI APIs?

Because AI should not hide broken business logic.

I first validated:

```text
orders
tickets
policies
health
validation
```

with deterministic tests.

Then the agent reused those capabilities.

---

# 3. What Is RAG?

RAG means Retrieval-Augmented Generation.

```text
User Question
   ↓
Retrieve Trusted Context
   ↓
Pass Context to LLM
   ↓
Generate Grounded Answer
```

It reduces dependence on model memory.

---

# 4. How Did You Chunk Documents?

I originally tested word-based chunks but evaluation exposed incomplete fragments.

I moved to sentence-aware atomic chunks.

Benefit:

```text
complete evidence
better context relevancy
easier debugging
```

---

# 5. Why ChromaDB?

It provides local persistent vector search and metadata filtering.

It is convenient for a learning/portfolio project.

The key learning is vector retrieval quality, not the specific vendor.

---

# 6. What Embedding Model Did You Use?

```text
sentence-transformers/all-MiniLM-L6-v2
```

It produces 384-dimensional embeddings.

---

# 7. How Do You Test Retrieval?

I test:

```text
document loading
chunk structure
vector DB count
semantic retrieval
top-k
metadata filter
golden dataset accuracy
```

before evaluating generation.

---

# 8. Why Test Retrieval Separately?

Because:

```text
wrong retrieval
+
good LLM
=
wrong answer
```

Without retrieval tests, the generator can be blamed for a retriever defect.

---

# 9. What Is Faithfulness?

Faithfulness asks whether the generated answer is supported by the supplied context.

Unsupported claims reduce faithfulness.

---

# 10. What Is Answer Relevancy?

It measures whether the answer actually addresses the user's question.

An answer can be factually correct but irrelevant.

---

# 11. What Is Contextual Precision?

It measures whether relevant retrieved context is ranked appropriately relative to irrelevant context.

---

# 12. What Is Contextual Recall?

It measures whether enough required supporting information was retrieved.

---

# 13. Why Use a Different Evaluation Model?

Generator:

```text
llama3.2
```

Evaluator:

```text
qwen3:4b-instruct
```

Using an independent judge reduces self-evaluation correlation.

---

# 14. How Did You Calibrate the Evaluator?

I tested it with:

```text
known good answer
known intentionally bad answer
```

The good case should pass and the bad case should fail.

---

# 15. Would You Lower a DeepEval Threshold if a Test Fails?

No.

I first investigate:

```text
retrieval
prompt
answer
dataset
judge calibration
```

Threshold changes should reflect business decisions, not green-build pressure.

---

# 16. What Is LangGraph Used For?

LangGraph models the support agent as an explicit state machine.

Supported intents:

```text
policy
order
ticket
order_policy
unsupported
```

Each intent has a controlled path.

---

# 17. Why Not Use One Big Agent Prompt?

A giant prompt gives the model too much uncontrolled responsibility.

An explicit graph gives:

```text
predictable paths
clear tool boundaries
testable state
better security
better observability
```

---

# 18. What Is Hybrid Routing?

High-confidence business patterns use deterministic routing.

Ambiguous requests can use an LLM.

Benefits:

```text
lower cost
lower latency
less flakiness
more testability
```

---

# 19. How Do You Ground Order IDs?

I extract them from the user's input with deterministic regex.

The LLM is not allowed to invent an order ID.

---

# 20. What Is Query Decomposition?

Example:

```text
Can I return ORD-1001?
```

contains two domains.

I split the need:

```text
ORD-1001 → order tool
return window → RAG
```

This improves retrieval quality.

---

# 21. How Do You Test an Agent?

I validate:

```text
intent
tool selection
tool sequence
arguments
trajectory
task completion
required final facts
```

not only final prose.

---

# 22. Tool Success vs Task Success?

Example:

```text
order_lookup executes successfully
ORD-9999 not found
```

The tool completed, but the user task did not.

So:

```text
task_completed = false
```

---

# 23. What Is Agent Trajectory?

It is the recorded path through the agent.

Example:

```text
router:order_policy
tool:order
tool:rag
finalize
```

It helps prove how the result was produced.

---

# 24. Why LangSmith?

LangSmith provides:

```text
traces
tool visibility
dataset experiments
regression comparison
```

It found real route and answer-fact issues during the project.

---

# 25. What LangSmith Evaluators Did You Use?

```text
intent_match
tool_sequence_match
task_completion_match
answer_contains_required_facts
approved_tools_only
```

These are deterministic evaluators.

---

# 26. Why Use Deterministic LangSmith Evaluators?

Because exact facts should not require an LLM judge.

For example:

```text
expected tool = order_lookup
```

is a normal equality comparison.

---

# 27. How Do You Prevent Prompt Injection?

I block known injection patterns before the model/tool layer.

I do not rely only on the system prompt.

---

# 28. How Do You Protect Secrets?

I use input and output scanning/redaction for:

```text
API keys
bearer tokens
named secrets
email
phone
payment card
```

High-risk output leakage is blocked.

---

# 29. What Is Least Privilege in an AI Agent?

Each intent has only the minimum authorized tool sequence.

Example:

```text
policy → RAG only
order → order lookup only
unsupported → no tools
```

---

# 30. Who Decides Tool Permission?

Deterministic application code.

Not the LLM.

Authorization happens immediately before tool execution.

---

# 31. How Do You Validate Tool Arguments?

Examples:

```text
order ID format
question not empty
length limits
ticket description
optional order ID
unsafe internal prompt content
```

---

# 32. What Is HITL?

Human-in-the-Loop.

Side-effecting actions require explicit approval.

Example:

```text
ticket_create
```

cannot execute until:

```text
approve_write = true
```

---

# 33. Why Is Ticket Creation Treated Differently?

Because it changes system state.

Reads and writes have different risk.

---

# 34. How Do You Test Security?

I keep an adversarial dataset with safe and attack cases.

The security gate requires 100% deterministic pass rate.

---

# 35. Why Include Safe Cases in Security Dataset?

To detect false positives.

A security system that blocks legitimate users is also defective.

---

# 36. How Do You Test the Browser UI?

With Playwright TypeScript.

I validate:

```text
form
payload
answer
intent
security status
tool calls
trajectory
HITL approval
```

---

# 37. Why Mock the AI API in Most UI Tests?

To keep browser regression deterministic.

UI correctness should not depend on Ollama/model latency.

---

# 38. Do You Still Have Real E2E?

Yes.

A separate live-backend test covers:

```text
browser
→ real UI
→ FastAPI
→ secure agent
→ real tool
```

---

# 39. What Was a Real Playwright Failure You Found?

A text locator:

```typescript
getByText('Blocked')
```

matched both the status badge and a trajectory item.

Playwright strict mode failed.

I replaced it with a locator targeting the intended status element.

---

# 40. What Is Playwright MCP?

It exposes browser capabilities through MCP so an AI agent can interact with the browser.

I use normal Playwright for repeatable regression and MCP for autonomous/exploratory testing.

---

# 41. Does MCP Replace Playwright Tests?

No.

MCP is goal-driven and exploratory.

Playwright Test remains the deterministic regression suite.

---

# 42. What Runs in CI?

Every PR runs:

```text
deterministic pytest
security gate
TypeScript compiler
mocked Playwright E2E
```

---

# 43. Why Not Run DeepEval on Every PR?

Local semantic evaluation requires:

```text
Ollama model
more compute
more latency
```

It can run in a dedicated semantic quality job or pre-release process.

---

# 44. What Is the Final Release Gate?

One script runs:

```text
Python deterministic regression
security hard gate
TypeScript compile
Playwright E2E
```

If any step fails, release fails.

---

# 45. What Is Your Main AI Testing Philosophy?

> Do not test AI as one black box. Test business logic, retrieval, generation, agent behavior, security and user experience as separate quality boundaries, then combine them in a small number of end-to-end gates.

---

# 46. Scenario: RAG Answer Is Wrong. What Do You Check First?

1. Query vector DB manually.
2. Verify retrieved policy.
3. Verify chunk quality.
4. Verify metadata filter.
5. Verify prompt context.
6. Only then inspect LLM generation.

---

# 47. Scenario: Final Answer Looks Correct but Wrong Tool Was Used

Fail the test.

The agent path matters because the wrong tool could:

```text
cost more
leak data
cause side effects
be unauthorized
```

---

# 48. Scenario: Security Prompt Gets a Refusal but Tool Executed First

That is a critical failure.

Security success means:

```text
attack blocked before capability execution
```

not merely:

```text
final text sounds safe
```

---

# 49. Scenario: Unknown Order Tool Returns Not Found

Expected:

```text
tool call attempted
task_completed = false
```

This is not a test failure if business behavior is correct.

---

# 50. Final Interview Summary

If asked what makes this project senior-level, emphasize:

```text
layered testing
deterministic vs semantic decision making
agent trajectory evaluation
tool security
HITL
observability
release gates
real defect investigation
```

Those concepts matter more than simply naming frameworks.
