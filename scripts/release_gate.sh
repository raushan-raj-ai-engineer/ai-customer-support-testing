#!/usr/bin/env bash

set -euo pipefail


# =========================================================
# PROJECT ROOT
# =========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"


# =========================================================
# HEADER
# =========================================================

echo
echo "=============================================="
echo "AI CUSTOMER SUPPORT FINAL RELEASE GATE"
echo "=============================================="


# =========================================================
# CHECK PYTHON ENVIRONMENT
# =========================================================

if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
fi


# =========================================================
# STEP 1
# PYTHON DETERMINISTIC REGRESSION
# =========================================================

echo
echo "[1/4] Python deterministic regression"
echo

pytest \
    -v \
    -m "not live_llm and not deepeval and not live_agent and not live_langsmith"


# =========================================================
# STEP 2
# SECURITY QUALITY GATE
# =========================================================

echo
echo "[2/4] Security quality gate"
echo

python \
    -m scripts.run_security_gate


# =========================================================
# STEP 3
# TYPESCRIPT COMPILE CHECK
# =========================================================

echo
echo "[3/4] TypeScript compile check"
echo

npx tsc --noEmit


# =========================================================
# STEP 4
# PLAYWRIGHT E2E
# =========================================================

echo
echo "[4/4] Playwright browser tests"
echo

npm run test:e2e


# =========================================================
# SUCCESS
# =========================================================

echo
echo "=============================================="
echo "FINAL RELEASE GATE: PASSED"
echo "=============================================="
echo
echo "Python regression : PASS"
echo "Security gate     : PASS"
echo "TypeScript        : PASS"
echo "Playwright E2E    : PASS"
echo
echo "=============================================="