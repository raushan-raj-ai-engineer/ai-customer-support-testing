import {
    expect,
    test,
} from '@playwright/test';

import {
    stepWithScreenshot,
} from './utils/step-with-screenshot';


interface TicketRequestBody {
    message: string;
    approve_write: boolean;
}


test.describe(
    'Human approval flow',
    () => {
        test(
            'ticket write request sends approval state',
            async (
                {
                    page,
                },
                testInfo,
            ) => {
                const requests:
                    TicketRequestBody[] =
                    [];


                // ============================================
                // MOCK SECURE AGENT
                // ============================================

                await page.route(
                    '**/api/v1/secure-agent/chat',
                    async (route) => {
                        const body:
                            TicketRequestBody =
                            route
                                .request()
                                .postDataJSON();

                        requests.push(
                            body,
                        );


                        // ========================================
                        // FIRST REQUEST
                        // WITHOUT APPROVAL
                        // ========================================

                        if (
                            !body.approve_write
                        ) {
                            await route.fulfill({
                                status:
                                    200,

                                contentType:
                                    'application/json',

                                body:
                                    JSON.stringify({
                                        message:
                                            body.message,

                                        intent:
                                            'ticket',

                                        answer:
                                            'I can create the support ticket, but the write action requires explicit approval.',

                                        tool_calls:
                                            [],

                                        trajectory: [
                                            'router:ticket',
                                            'security:write_approval_required',
                                        ],

                                        task_completed:
                                            false,

                                        blocked:
                                            true,

                                        security_findings: [
                                            {
                                                rule_id:
                                                    'SEC-WRITE-001',

                                                category:
                                                    'write_approval',

                                                severity:
                                                    'medium',

                                                message:
                                                    'Ticket creation requires explicit approval.',
                                            },
                                        ],

                                        error:
                                            null,
                                    }),
                            });

                            return;
                        }


                        // ========================================
                        // SECOND REQUEST
                        // WITH APPROVAL
                        // ========================================

                        await route.fulfill({
                            status:
                                200,

                            contentType:
                                'application/json',

                            body:
                                JSON.stringify({
                                    message:
                                        body.message,

                                    intent:
                                        'ticket',

                                    answer:
                                        'Support ticket TKT-9001 was created successfully.',

                                    tool_calls: [
                                        {
                                            name:
                                                'ticket_create',

                                            input: {
                                                description:
                                                    body.message,

                                                order_id:
                                                    null,
                                            },

                                            success:
                                                true,

                                            output: {
                                                ticket_id:
                                                    'TKT-9001',
                                            },

                                            error:
                                                null,
                                        },
                                    ],

                                    trajectory: [
                                        'router:ticket',
                                        'tool:ticket',
                                        'finalize',
                                    ],

                                    task_completed:
                                        true,

                                    blocked:
                                        false,

                                    security_findings:
                                        [],

                                    error:
                                        null,
                                }),
                        });
                    },
                );


                const question =
                    'Create a ticket because my shipment is delayed.';

                const questionInput =
                    page.getByLabel(
                        'Your question',
                    );

                const submitButton =
                    page.getByRole(
                        'button',
                        {
                            name:
                                'Ask support agent',
                        },
                    );

                const approvalCheckbox =
                    page.getByLabel(
                        /Approve write actions/i,
                    );

                const securityStatus =
                    page.locator(
                        '#security-status',
                    );

                const answer =
                    page.locator(
                        '#answer',
                    );


                // ============================================
                // OPEN
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '01 Open support page',
                    async () => {
                        await page.goto('/');
                    },
                );


                // ============================================
                // ENTER TICKET REQUEST
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '02 Enter ticket request',
                    async () => {
                        await questionInput.fill(
                            question,
                        );
                    },
                );


                // ============================================
                // SUBMIT WITHOUT APPROVAL
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '03 Submit without write approval',
                    async () => {
                        await submitButton.click();
                    },
                );


                // ============================================
                // VERIFY BLOCKED
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '04 Verify write request blocked',
                    async () => {
                        await expect(
                            answer,
                        ).toContainText(
                            'requires explicit approval',
                        );

                        await expect(
                            securityStatus,
                        ).toHaveText(
                            'Blocked',
                        );
                    },
                );


                // ============================================
                // SECURITY FINDING
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '05 Verify write approval finding',
                    async () => {
                        await expect(
                            page.getByText(
                                /SEC-WRITE-001/,
                            ),
                        ).toBeVisible();
                    },
                );


                // ============================================
                // NO TOOL
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '06 Verify no write tool executed',
                    async () => {
                        await expect(
                            page.getByText(
                                'No tools executed',
                                {
                                    exact:
                                        true,
                                },
                            ),
                        ).toBeVisible();
                    },
                );


                // ============================================
                // APPROVE
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '07 Enable write approval',
                    async () => {
                        await approvalCheckbox.check();

                        await expect(
                            approvalCheckbox,
                        ).toBeChecked();
                    },
                );


                // ============================================
                // RETRY
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '08 Submit approved ticket request',
                    async () => {
                        await submitButton.click();
                    },
                );


                // ============================================
                // VERIFY TICKET
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '09 Verify ticket created',
                    async () => {
                        await expect(
                            answer,
                        ).toContainText(
                            'TKT-9001',
                        );
                    },
                );


                // ============================================
                // VERIFY ALLOWED
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '10 Verify approved request allowed',
                    async () => {
                        await expect(
                            securityStatus,
                        ).toHaveText(
                            'Allowed',
                        );
                    },
                );


                // ============================================
                // VERIFY TOOL
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '11 Verify ticket tool succeeded',
                    async () => {
                        await expect(
                            page.getByText(
                                'ticket_create — success',
                                {
                                    exact:
                                        true,
                                },
                            ),
                        ).toBeVisible();
                    },
                );


                // ============================================
                // REQUEST CONTRACT ASSERTIONS
                // ============================================

                expect(
                    requests,
                ).toHaveLength(
                    2,
                );

                expect(
                    requests[0],
                ).toEqual({
                    message:
                        question,

                    approve_write:
                        false,
                });

                expect(
                    requests[1],
                ).toEqual({
                    message:
                        question,

                    approve_write:
                        true,
                });
            },
        );
    },
);