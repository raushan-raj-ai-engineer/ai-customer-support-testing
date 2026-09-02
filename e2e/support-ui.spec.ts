import {
    expect,
    test,
} from '@playwright/test';

import {
    stepWithScreenshot,
} from './utils/step-with-screenshot';


test.describe(
    'AI Support UI',
    () => {
        test(
            'renders accessible support form',
            async (
                {
                    page,
                },
                testInfo,
            ) => {
                await stepWithScreenshot(
                    page,
                    testInfo,
                    '01 Open support page',
                    async () => {
                        await page.goto('/');
                    },
                );


                await stepWithScreenshot(
                    page,
                    testInfo,
                    '02 Verify page heading',
                    async () => {
                        await expect(
                            page.getByRole(
                                'heading',
                                {
                                    name:
                                        'AI Customer Support',
                                },
                            ),
                        ).toBeVisible();
                    },
                );


                await stepWithScreenshot(
                    page,
                    testInfo,
                    '03 Verify question input',
                    async () => {
                        await expect(
                            page.getByLabel(
                                'Your question',
                            ),
                        ).toBeVisible();
                    },
                );


                await stepWithScreenshot(
                    page,
                    testInfo,
                    '04 Verify write approval checkbox',
                    async () => {
                        await expect(
                            page.getByLabel(
                                /Approve write actions/i,
                            ),
                        ).toBeVisible();
                    },
                );


                await stepWithScreenshot(
                    page,
                    testInfo,
                    '05 Verify submit button',
                    async () => {
                        await expect(
                            page.getByRole(
                                'button',
                                {
                                    name:
                                        'Ask support agent',
                                },
                            ),
                        ).toBeVisible();
                    },
                );
            },
        );


        test(
            'submits shipping question and displays agent result',
            async (
                {
                    page,
                },
                testInfo,
            ) => {
                let requestBody:
                    | {
                        message: string;
                        approve_write: boolean;
                    }
                    | undefined;


                // ============================================
                // MOCK SECURE AGENT API
                // ============================================

                await page.route(
                    '**/api/v1/secure-agent/chat',
                    async (route) => {
                        requestBody =
                            route
                                .request()
                                .postDataJSON();

                        await route.fulfill({
                            status: 200,
                            contentType:
                                'application/json',

                            body: JSON.stringify({
                                message:
                                    requestBody?.message ??
                                    '',

                                intent:
                                    'policy',

                                answer:
                                    'Standard shipping normally takes 3 to 5 business days.',

                                tool_calls: [
                                    {
                                        name:
                                            'rag_policy_lookup',

                                        input: {
                                            question:
                                                'How long does standard shipping take?',
                                        },

                                        success:
                                            true,

                                        output: {
                                            policy_ids: [
                                                'SHIPPING_POLICY',
                                            ],
                                        },

                                        error:
                                            null,
                                    },
                                ],

                                trajectory: [
                                    'router:policy',
                                    'tool:rag',
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


                // ============================================
                // STEP 1
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
                // STEP 2
                // ============================================

                const question =
                    'How long does standard shipping take?';

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '02 Enter shipping question',
                    async () => {
                        await page
                            .getByLabel(
                                'Your question',
                            )
                            .fill(
                                question,
                            );
                    },
                );


                // ============================================
                // STEP 3
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '03 Submit support question',
                    async () => {
                        await page
                            .getByRole(
                                'button',
                                {
                                    name:
                                        'Ask support agent',
                                },
                            )
                            .click();
                    },
                );


                // ============================================
                // STEP 4
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '04 Verify shipping answer',
                    async () => {
                        await expect(
                            page.locator(
                                '#answer',
                            ),
                        ).toContainText(
                            '3 to 5 business days',
                        );
                    },
                );


                // ============================================
                // STEP 5
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '05 Verify policy intent',
                    async () => {
                        await expect(
                            page.getByText(
                                'policy',
                                {
                                    exact: true,
                                },
                            ),
                        ).toBeVisible();
                    },
                );


                // ============================================
                // STEP 6
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '06 Verify request allowed',
                    async () => {
                        await expect(
                            page.locator(
                                '#security-status',
                            ),
                        ).toHaveText(
                            'Allowed',
                        );
                    },
                );


                // ============================================
                // STEP 7
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '07 Verify RAG tool execution',
                    async () => {
                        await expect(
                            page.getByText(
                                'rag_policy_lookup — success',
                                {
                                    exact: true,
                                },
                            ),
                        ).toBeVisible();
                    },
                );


                // ============================================
                // STEP 8
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '08 Verify agent trajectory',
                    async () => {
                        await expect(
                            page.getByText(
                                'router:policy',
                                {
                                    exact: true,
                                },
                            ),
                        ).toBeVisible();

                        await expect(
                            page.getByText(
                                'tool:rag',
                                {
                                    exact: true,
                                },
                            ),
                        ).toBeVisible();

                        await expect(
                            page.getByText(
                                'finalize',
                                {
                                    exact: true,
                                },
                            ),
                        ).toBeVisible();
                    },
                );


                // ============================================
                // REQUEST CONTRACT
                // ============================================

                expect(
                    requestBody,
                ).toEqual({
                    message:
                        question,

                    approve_write:
                        false,
                });
            },
        );


        test(
            'example button populates question',
            async (
                {
                    page,
                },
                testInfo,
            ) => {
                await stepWithScreenshot(
                    page,
                    testInfo,
                    '01 Open support page',
                    async () => {
                        await page.goto('/');
                    },
                );


                await stepWithScreenshot(
                    page,
                    testInfo,
                    '02 Click order example',
                    async () => {
                        await page
                            .getByRole(
                                'button',
                                {
                                    name:
                                        /ORD-1001/i,
                                },
                            )
                            .click();
                    },
                );


                await stepWithScreenshot(
                    page,
                    testInfo,
                    '03 Verify example question populated',
                    async () => {
                        await expect(
                            page.getByLabel(
                                'Your question',
                            ),
                        ).toHaveValue(
                            'Where is ORD-1001?',
                        );
                    },
                );
            },
        );
    },
);