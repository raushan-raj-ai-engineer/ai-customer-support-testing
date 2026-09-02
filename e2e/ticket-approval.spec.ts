import { expect, test } from '@playwright/test';

interface TicketRequestBody {
    message: string;
    approve_write: boolean;
}

test.describe('Human approval flow', () => {
    test(
        'ticket write request sends approval state',
        async ({ page }) => {
            const requests: TicketRequestBody[] = [];

            await page.route(
                '**/api/v1/secure-agent/chat',
                async (route) => {
                    const body: TicketRequestBody =
                        route.request().postDataJSON();

                    requests.push(body);

                    if (!body.approve_write) {
                        await route.fulfill({
                            status: 200,
                            contentType: 'application/json',
                            body: JSON.stringify({
                                message: body.message,

                                intent: 'ticket',

                                answer:
                                    'I can create the support ticket, ' +
                                    'but the write action requires explicit approval.',

                                tool_calls: [],

                                trajectory: [
                                    'router:ticket',
                                    'security:write_approval_required',
                                ],

                                task_completed: false,

                                blocked: true,

                                security_findings: [
                                    {
                                        rule_id: 'SEC-WRITE-001',
                                        category: 'write_approval',
                                        severity: 'medium',
                                        message:
                                            'Ticket creation requires explicit approval.',
                                    },
                                ],

                                error: null,
                            }),
                        });

                        return;
                    }

                    await route.fulfill({
                        status: 200,
                        contentType: 'application/json',
                        body: JSON.stringify({
                            message: body.message,

                            intent: 'ticket',

                            answer:
                                'Support ticket TKT-9001 ' +
                                'was created successfully.',

                            tool_calls: [
                                {
                                    name: 'ticket_create',

                                    input: {
                                        description: body.message,
                                        order_id: null,
                                    },

                                    success: true,

                                    output: {
                                        ticket_id: 'TKT-9001',
                                    },

                                    error: null,
                                },
                            ],

                            trajectory: [
                                'router:ticket',
                                'tool:ticket',
                                'finalize',
                            ],

                            task_completed: true,

                            blocked: false,

                            security_findings: [],

                            error: null,
                        }),
                    });
                },
            );

            await page.goto('/');

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

            // =====================================
            // FIRST REQUEST — NO APPROVAL
            // =====================================

            await questionInput.fill(
                question,
            );

            await submitButton.click();

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

            await expect(
                page.getByText(
                    'No tools executed',
                    {
                        exact: true,
                    },
                ),
            ).toBeVisible();

            await expect(
                page.getByText(
                    /SEC-WRITE-001/,
                ),
            ).toBeVisible();

            // =====================================
            // SECOND REQUEST — APPROVED
            // =====================================

            await approvalCheckbox.check();

            await submitButton.click();

            await expect(
                answer,
            ).toContainText(
                'TKT-9001',
            );

            await expect(
                securityStatus,
            ).toHaveText(
                'Allowed',
            );

            await expect(
                page.getByText(
                    'ticket_create — success',
                    {
                        exact: true,
                    },
                ),
            ).toBeVisible();

            // =====================================
            // REQUEST VALIDATION
            // =====================================

            expect(
                requests,
            ).toHaveLength(
                2,
            );

            expect(
                requests[0].message,
            ).toBe(
                question,
            );

            expect(
                requests[0].approve_write,
            ).toBe(
                false,
            );

            expect(
                requests[1].message,
            ).toBe(
                question,
            );

            expect(
                requests[1].approve_write,
            ).toBe(
                true,
            );
        },
    );
});