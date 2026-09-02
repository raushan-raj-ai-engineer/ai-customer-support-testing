#!/usr/bin/env bash

set -u

# ============================================================
# AI CUSTOMER SUPPORT - FULL AI QUALITY SHOWCASE
#
# Unified evidence:
# - deterministic pytest
# - RAG tests
# - agent tests
# - security tests
# - DeepEval / live LLM tests
# - live LangGraph agent tests
# - optional LangSmith tests / experiment
# - Playwright E2E + screenshots
# - master Allure report
#
# Important:
# Individual layers may fail without immediately stopping the
# script so that Allure evidence can still be generated.
# The final exit code remains non-zero if any required layer
# failed.
# ============================================================


# ============================================================
# PROJECT ROOT
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"


# ============================================================
# PYTHON ENVIRONMENT
# ============================================================

if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
fi


# ============================================================
# CONFIGURATION
# ============================================================

ALLURE_RESULTS_DIR="${ALLURE_RESULTS_DIR:-allure-results}"
ALLURE_REPORT_DIR="${ALLURE_REPORT_DIR:-allure-report}"
SHOWCASE_ARTIFACTS_DIR="${SHOWCASE_ARTIFACTS_DIR:-artifacts/quality-showcase}"

# High-level showcase toggles.
RUN_DEEPEVAL="${RUN_DEEPEVAL:-1}"
RUN_LIVE_AGENT="${RUN_LIVE_AGENT:-1}"
RUN_LANGSMITH="${RUN_LANGSMITH:-0}"
RUN_PLAYWRIGHT="${RUN_PLAYWRIGHT:-1}"

# These are the environment variables checked by the actual
# live pytest modules.
#
# If the caller does not explicitly provide them, inherit the
# corresponding showcase toggle.
RUN_LIVE_LLM="${RUN_LIVE_LLM:-${RUN_DEEPEVAL}}"
RUN_LIVE_LANGSMITH="${RUN_LIVE_LANGSMITH:-${RUN_LANGSMITH}}"

# CRITICAL:
# pytest skip conditions read os.environ, so defaults created
# inside this script MUST be exported.
export RUN_DEEPEVAL
export RUN_LIVE_LLM
export RUN_LIVE_AGENT
export RUN_LIVE_LANGSMITH

export ALLURE_RESULTS_DIR


# ============================================================
# SHOW EFFECTIVE CONFIGURATION
# ============================================================

echo
echo "============================================================"
echo "FULL AI QUALITY SHOWCASE CONFIGURATION"
echo "============================================================"
echo
echo "RUN_DEEPEVAL        = ${RUN_DEEPEVAL}"
echo "RUN_LIVE_LLM        = ${RUN_LIVE_LLM}"
echo "RUN_LIVE_AGENT      = ${RUN_LIVE_AGENT}"
echo "RUN_LANGSMITH       = ${RUN_LANGSMITH}"
echo "RUN_LIVE_LANGSMITH  = ${RUN_LIVE_LANGSMITH}"
echo "RUN_PLAYWRIGHT      = ${RUN_PLAYWRIGHT}"
echo
echo "Allure results      = ${ALLURE_RESULTS_DIR}"
echo "Allure report       = ${ALLURE_REPORT_DIR}"
echo "Raw evidence        = ${SHOWCASE_ARTIFACTS_DIR}"
echo "============================================================"


# ============================================================
# CLEAN OUTPUT
# ============================================================

rm -rf \
    "${ALLURE_RESULTS_DIR}" \
    "${ALLURE_REPORT_DIR}" \
    "${SHOWCASE_ARTIFACTS_DIR}"

mkdir -p \
    "${ALLURE_RESULTS_DIR}" \
    "${SHOWCASE_ARTIFACTS_DIR}"


# ============================================================
# STATUS TRACKING
# ============================================================

overall_status=0


run_step() {
    local step_name="$1"
    shift

    echo
    echo "============================================================"
    echo "${step_name}"
    echo "============================================================"
    echo

    "$@"
    local step_status=$?

    if [[ ${step_status} -ne 0 ]]; then
        echo
        echo "[FAILED] ${step_name}"
        overall_status=1
    else
        echo
        echo "[PASSED] ${step_name}"
    fi

    # Continue so final report/evidence can still be generated.
    return 0
}


run_logged_step() {
    local step_name="$1"
    local log_file="$2"
    shift 2

    echo
    echo "============================================================"
    echo "${step_name}"
    echo "============================================================"
    echo

    mkdir -p "$(dirname "${log_file}")"

    set -o pipefail
    "$@" 2>&1 | tee "${log_file}"
    local step_status=$?
    set +o pipefail

    if [[ ${step_status} -ne 0 ]]; then
        echo
        echo "[FAILED] ${step_name}"
        overall_status=1
    else
        echo
        echo "[PASSED] ${step_name}"
    fi

    return 0
}


# ============================================================
# 1. VECTOR DATABASE
# ============================================================

run_step \
    "Build vector database" \
    python -m scripts.build_vector_db


# ============================================================
# 2. DETERMINISTIC PYTHON / RAG / AGENT / SECURITY
# ============================================================

run_step \
    "Deterministic Python / RAG / Agent / Security tests" \
    python -m pytest \
        -p tests.allure_plugin \
        -v \
        -m "not live_llm and not deepeval and not live_agent and not live_langsmith" \
        --alluredir "${ALLURE_RESULTS_DIR}"


# ============================================================
# 3. SECURITY QUALITY GATE
# ============================================================

run_logged_step \
    "Security deterministic quality gate" \
    "${SHOWCASE_ARTIFACTS_DIR}/security-gate.log" \
    python -m scripts.run_security_gate


# ============================================================
# 4. DEEPEVAL + LIVE RAG/LLM
# ============================================================

if [[ "${RUN_DEEPEVAL}" == "1" ]]; then
    run_step \
        "DeepEval / Live LLM quality tests" \
        python -m pytest \
            -p tests.allure_plugin \
            -v \
            -m "deepeval or live_llm" \
            --alluredir "${ALLURE_RESULTS_DIR}"
else
    echo
    echo "[SKIPPED] DeepEval / Live LLM quality tests"
fi


# ============================================================
# 5. LIVE LANGGRAPH AGENT
# ============================================================

if [[ "${RUN_LIVE_AGENT}" == "1" ]]; then
    run_step \
        "Live LangGraph agent tests" \
        python -m pytest \
            -p tests.allure_plugin \
            -v \
            -m "live_agent" \
            --alluredir "${ALLURE_RESULTS_DIR}"
else
    echo
    echo "[SKIPPED] Live LangGraph agent tests"
fi


# ============================================================
# 6. LANGSMITH
# ============================================================

if [[ "${RUN_LANGSMITH}" == "1" ]]; then
    run_step \
        "Live LangSmith pytest tests" \
        python -m pytest \
            -p tests.allure_plugin \
            -v \
            -m "live_langsmith" \
            --alluredir "${ALLURE_RESULTS_DIR}"

    run_logged_step \
        "LangSmith offline experiment" \
        "${SHOWCASE_ARTIFACTS_DIR}/langsmith-experiment.log" \
        python -m scripts.run_langsmith_experiment
else
    echo
    echo "[SKIPPED] LangSmith live tests and experiment"
fi


# ============================================================
# 7. TYPESCRIPT
# ============================================================

run_step \
    "TypeScript compile check" \
    npx tsc --noEmit


# ============================================================
# 8. PLAYWRIGHT + SCREENSHOTS + ALLURE
# ============================================================

if [[ "${RUN_PLAYWRIGHT}" == "1" ]]; then
    run_step \
        "Playwright E2E with Allure and screenshots" \
        npx playwright test \
            --config=playwright.allure.config.ts
else
    echo
    echo "[SKIPPED] Playwright E2E"
fi


# ============================================================
# 9. ALLURE ENVIRONMENT METADATA
# ============================================================

run_step \
    "Write Allure environment metadata" \
    python -m scripts.write_allure_environment


# ============================================================
# 10. GENERATE MASTER ALLURE REPORT
#
# Allure Report 3 does NOT support the old --clean flag used
# by Allure Report 2 in the same way.
#
# The report directory was already removed at script startup,
# so --clean is unnecessary.
# ============================================================

if npx allure --version >/dev/null 2>&1; then
    run_step \
        "Generate master Allure HTML report" \
        npx allure generate \
            "${ALLURE_RESULTS_DIR}" \
            --output "${ALLURE_REPORT_DIR}"
else
    echo
    echo "[FAILED] Allure CLI is not available."
    echo
    echo "Install it with:"
    echo
    echo "  npm install -D allure"
    echo
    overall_status=1
fi


# ============================================================
# FINAL SUMMARY
# ============================================================

echo
echo "============================================================"
echo "FULL AI QUALITY SHOWCASE"
echo "============================================================"
echo
echo "Allure results : ${ALLURE_RESULTS_DIR}"
echo "Allure report  : ${ALLURE_REPORT_DIR}"
echo "Raw evidence   : ${SHOWCASE_ARTIFACTS_DIR}"
echo

if [[ ${overall_status} -eq 0 ]]; then
    echo "FINAL SHOWCASE GATE: PASSED"
else
    echo "FINAL SHOWCASE GATE: FAILED"
fi

echo
echo "============================================================"
echo


# ============================================================
# FINAL EXIT CODE
# ============================================================

exit "${overall_status}"
