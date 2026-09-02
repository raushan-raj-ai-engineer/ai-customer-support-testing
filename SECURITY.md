# Security Policy and AI Guardrail Design

## 1. Scope

This repository demonstrates application-layer security controls for an AI customer-support agent.

It is a learning project and should not be treated as a complete enterprise security product.

---

# 2. Security Principles

## Do Not Trust the LLM as a Security Boundary

The system prompt is not authorization.

Actual security decisions are enforced in deterministic application code.

---

## Least Privilege

Each intent receives only the minimum required tools.

```text
policy       → RAG
order        → order lookup
ticket       → ticket create
order_policy → order lookup + RAG
unsupported  → none
```

---

## Complete Mediation

Authorization occurs immediately before tool execution.

A previously approved route does not automatically make all later tool calls safe.

---

## Human Approval for Writes

Side-effecting actions require explicit approval.

Current example:

```text
ticket_create
```

---

## Defense in Depth

Security exists at multiple boundaries:

```text
input
tool arguments
tool authorization
actual tool history
output
```

---

# 3. Threats Covered

The deterministic security layer tests:

```text
direct prompt injection
system prompt extraction
developer prompt extraction
guardrail bypass
secret extraction
environment variable extraction
unauthorized tool invocation
tool argument manipulation
PII leakage
credential leakage
output leakage
write-without-approval
```

---

# 4. Input Guard

Before AI execution, `InputGuard` checks:

```text
empty input
length limits
prompt injection patterns
prompt leakage attempts
tool manipulation
secret extraction
```

Sensitive but legitimate input may be redacted and allowed.

---

# 5. Redaction

The project detects/redacts categories such as:

```text
email
phone
payment card
API key
named secret
bearer token
```

Example:

```text
rohit@example.com
```

becomes:

```text
[REDACTED_EMAIL]
```

---

# 6. Tool Authorization

`ToolPolicy` verifies:

```text
intent
expected next tool
executed tool history
write approval
arguments
```

Unknown or duplicate tools are rejected.

---

# 7. Output Guard

Output is inspected for:

```text
credential leakage
environment variable leakage
prompt/developer leakage
sensitive data
```

Critical leakage returns a safe fallback.

---

# 8. Security Dataset

The adversarial dataset contains:

```text
safe cases
attack cases
```

Safe cases protect against false positives.

Attack cases protect against false negatives.

---

# 9. Security Quality Gate

Run:

```bash
python -m scripts.run_security_gate
```

Target:

```text
100%
```

Known deterministic security cases should all pass.

---

# 10. Reporting a Security Issue

If this repository is public and you identify a security issue:

1. Do not include real credentials.
2. Do not publish active secrets in an issue.
3. Provide a minimal reproducible example.
4. Identify the affected layer:
   - input guard,
   - redaction,
   - tool policy,
   - secure agent,
   - output guard,
   - UI.
5. Include expected safe behavior.

For a real production deployment, configure a private vulnerability-reporting channel.

---

# 11. Known Limitations

The current deterministic guardrails are pattern/rule based.

They do not guarantee detection of every possible:

```text
obfuscated prompt injection
multi-turn attack
indirect injection
unicode attack
novel jailbreak
cross-language attack
retrieved-document injection
```

Future improvements may include:

```text
indirect prompt-injection filtering
context provenance
policy engine
structured tool scopes
tenant authorization
authentication
rate limits
audit storage
SIEM integration
advanced classifiers
multilingual attack datasets
```

---

# 12. Secrets

Never commit:

```text
LANGSMITH_API_KEY
OPENAI_API_KEY
HF_TOKEN
passwords
tokens
private certificates
database credentials
```

Use:

```text
.env.example
```

for variable names only.

---

# 13. Production Note

Before real deployment, add:

```text
authentication
authorization
tenant isolation
persistent audit logs
rate limiting
secret manager
TLS
production database controls
dependency scanning
container scanning
monitoring/alerting
```

This repository demonstrates AI-specific security concepts, not the entire enterprise security stack.
