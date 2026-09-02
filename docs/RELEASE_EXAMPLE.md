# Example Successful Release

Use this document to understand what "green" means.

---

## 1. Deterministic Python Gate

Expected pattern:

```text
tests/agent/... PASSED
tests/rag/... PASSED
tests/security/... PASSED
tests/test_health.py PASSED
tests/test_orders.py PASSED
tests/test_policies.py PASSED
tests/test_tickets.py PASSED
```

Live/semantic tests may be deselected by marker.

Warnings from dependencies do not necessarily mean failure.

---

## 2. Security Gate

Expected:

```text
Total:     <dataset count>
Passed:    <same count>
Failed:    0
Pass rate: 100.00%

SECURITY QUALITY GATE: PASSED
```

---

## 3. TypeScript

Command:

```bash
npx tsc --noEmit
```

Expected:

```text
no output
exit code 0
```

---

## 4. Playwright

Default suite should show deterministic UI/security/HITL tests passing.

Live backend may be skipped unless explicitly enabled.

Example shape:

```text
6 passed
1 skipped
```

The exact count can change when tests are added.

---

## 5. Final Script

Expected ending:

```text
==============================================
FINAL RELEASE GATE: PASSED
==============================================

Python regression : PASS
Security gate     : PASS
TypeScript        : PASS
Playwright E2E    : PASS
```

---

## 6. Important Rule

Do not compare only exact historical test counts.

A correct release means:

```text
all selected mandatory tests pass
all hard gates pass
no release-blocking security failure
no compile failure
no browser regression
```
