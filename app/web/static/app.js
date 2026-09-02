"use strict";


const form = document.getElementById(
    "support-form"
);

const messageInput = document.getElementById(
    "message-input"
);

const approveWrite = document.getElementById(
    "approve-write"
);

const sendButton = document.getElementById(
    "send-button"
);

const loading = document.getElementById(
    "loading"
);

const errorMessage = document.getElementById(
    "error-message"
);

const resultPanel = document.getElementById(
    "result-panel"
);

const intentValue = document.getElementById(
    "intent-value"
);

const taskValue = document.getElementById(
    "task-value"
);

const answerElement = document.getElementById(
    "answer"
);

const securityStatus = document.getElementById(
    "security-status"
);

const toolCallsElement = document.getElementById(
    "tool-calls"
);

const trajectoryElement = document.getElementById(
    "trajectory"
);

const securitySection = document.getElementById(
    "security-section"
);

const securityFindingsElement =
    document.getElementById(
        "security-findings"
    );


const endpoint = (
    "/api/v1/secure-agent/chat"
);


// =========================================================
// HELPERS
// =========================================================


function clearChildren(element) {

    while (
        element.firstChild
    ) {

        element.removeChild(
            element.firstChild
        );
    }
}


function appendListItem(
    element,
    text,
) {

    const item = (
        document.createElement(
            "li"
        )
    );

    item.textContent = (
        text
    );

    element.appendChild(
        item
    );
}


function setBusy(
    busy,
) {

    sendButton.disabled = (
        busy
    );

    messageInput.disabled = (
        busy
    );

    approveWrite.disabled = (
        busy
    );

    loading.hidden = (
        !busy
    );
}


function showError(
    message,
) {

    errorMessage.textContent = (
        message
    );

    errorMessage.hidden = false;

    resultPanel.hidden = true;
}


function clearError() {

    errorMessage.textContent = "";

    errorMessage.hidden = true;
}


// =========================================================
// SECURITY FINDINGS
// =========================================================


function renderSecurityFindings(
    findings,
) {

    clearChildren(
        securityFindingsElement
    );

    if (
        !Array.isArray(findings)
        || findings.length === 0
    ) {

        securitySection.hidden = true;

        return;
    }

    securitySection.hidden = false;

    for (
        const finding
        of findings
    ) {

        const ruleId = (
            finding.rule_id
            ?? "unknown"
        );

        const message = (
            finding.message
            ?? "Security finding"
        );

        const severity = (
            finding.severity
            ?? "unknown"
        );

        appendListItem(
            securityFindingsElement,

            (
                `${ruleId} `
                + `[${severity}] `
                + `${message}`
            ),
        );
    }
}


// =========================================================
// TOOL CALLS
// =========================================================


function renderToolCalls(
    toolCalls,
) {

    clearChildren(
        toolCallsElement
    );

    if (
        !Array.isArray(toolCalls)
        || toolCalls.length === 0
    ) {

        appendListItem(
            toolCallsElement,
            "No tools executed",
        );

        return;
    }

    for (
        const toolCall
        of toolCalls
    ) {

        const name = (
            toolCall.name
            ?? "unknown_tool"
        );

        const success = (
            toolCall.success
            === true
        );

        appendListItem(
            toolCallsElement,

            (
                `${name} — `
                + (
                    success
                        ? "success"
                        : "failed"
                )
            ),
        );
    }
}


// =========================================================
// TRAJECTORY
// =========================================================


function renderTrajectory(
    trajectory,
) {

    clearChildren(
        trajectoryElement
    );

    if (
        !Array.isArray(trajectory)
        || trajectory.length === 0
    ) {

        appendListItem(
            trajectoryElement,
            "No trajectory recorded",
        );

        return;
    }

    for (
        const step
        of trajectory
    ) {

        appendListItem(
            trajectoryElement,
            String(step),
        );
    }
}


// =========================================================
// RESULT
// =========================================================


function renderResult(
    result,
) {

    resultPanel.hidden = false;

    intentValue.textContent = (
        result.intent
        ?? "unknown"
    );

    taskValue.textContent = (
        result.task_completed
            ? "Yes"
            : "No"
    );

    answerElement.textContent = (
        result.answer
        ?? ""
    );

    const blocked = (
        result.blocked
        === true
    );

    securityStatus.textContent = (
        blocked
            ? "Blocked"
            : "Allowed"
    );

    securityStatus.dataset.status = (
        blocked
            ? "blocked"
            : "allowed"
    );

    renderToolCalls(
        result.tool_calls
    );

    renderTrajectory(
        result.trajectory
    );

    renderSecurityFindings(
        result.security_findings
    );
}


// =========================================================
// SUBMIT
// =========================================================


async function submitRequest(
    message,
) {

    clearError();

    setBusy(
        true
    );

    try {

        const response = await fetch(
            endpoint,

            {
                method: "POST",

                headers: {
                    "Content-Type": (
                        "application/json"
                    ),
                },

                body: JSON.stringify(
                    {
                        message,

                        approve_write: (
                            approveWrite
                                .checked
                        ),
                    }
                ),
            }
        );

        let payload;

        try {

            payload = await (
                response.json()
            );

        } catch {

            throw new Error(
                "Server returned "
                + "an invalid response."
            );
        }

        if (
            !response.ok
        ) {

            const detail = (
                payload.detail
                ?? "Request failed."
            );

            throw new Error(
                String(detail)
            );
        }

        renderResult(
            payload
        );

    } catch (
    error
    ) {

        const messageText = (
            error instanceof Error
                ? error.message
                : "Unexpected error"
        );

        showError(
            messageText
        );

    } finally {

        setBusy(
            false
        );
    }
}


// =========================================================
// FORM EVENT
// =========================================================


form.addEventListener(
    "submit",

    async (
        event
    ) => {

        event.preventDefault();

        const message = (
            messageInput.value
                .trim()
        );

        if (
            !message
        ) {

            showError(
                "Please enter a question."
            );

            messageInput.focus();

            return;
        }

        await submitRequest(
            message
        );
    }
);


// =========================================================
// EXAMPLE BUTTONS
// =========================================================


const exampleButtons = (
    document.querySelectorAll(
        "[data-question]"
    )
);


for (
    const button
    of exampleButtons
) {

    button.addEventListener(
        "click",

        () => {

            const question = (
                button.getAttribute(
                    "data-question"
                )
            );

            if (
                question
            ) {

                messageInput.value = (
                    question
                );

                messageInput.focus();
            }
        }
    );
}