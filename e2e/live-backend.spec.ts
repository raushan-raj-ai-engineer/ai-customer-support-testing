import {
    expect,
    test,
} from '@playwright/test';

import {
    stepWithScreenshot,
} from './utils/step-with-screenshot';


const runLiveBackend =
    process.env
        .RUN_LIVE_BACKEND_E2E ===
    '1';


const uiPath =
    process.env
        .PLAYWRIGHT_UI_PATH ??
    '/support';


test.describe(
    'Live secure backend',
    () => {
        test.skip(
            !runLiveBackend,
            'Set RUN_LIVE_BACKEND_E2E=1 to run live backend E2E tests.',
        );


        test(
            'real order lookup works end-to-end',
            async (
                {
                    page,
                },
                testInfo,
            ) => {
                // ============================================
                // OPEN REAL UI
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '01 Open live support UI',
                    async () => {
                        await page.goto(
                            uiPath,
                        );
                    },
                );


                // ============================================
                // ENTER ORDER
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '02 Enter real order lookup question',
                    async () => {
                        await page
                            .getByLabel(
                                'Your question',
                            )
                            .fill(
                                'Where is ORD-1001?',
                            );
                    },
                );


                // ============================================
                // SUBMIT
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '03 Submit real backend request',
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
                // ORDER ID
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '04 Verify real order response',
                    async () => {
                        await expect(
                            page.locator(
                                '#answer',
                            ),
                        ).toContainText(
                            'ORD-1001',
                            {
                                timeout:
                                    30_000,
                            },
                        );
                    },
                );


                // ============================================
                // STATUS
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '05 Verify shipped order status',
                    async () => {
                        await expect(
                            page.locator(
                                '#answer',
                            ),
                        ).toContainText(
                            'SHIPPED',
                        );
                    },
                );


                // ============================================
                // SECURITY
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '06 Verify real request allowed',
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
                // TOOL
                // ============================================

                await stepWithScreenshot(
                    page,
                    testInfo,
                    '07 Verify real order tool succeeded',
                    async () => {
                        await expect(
                            page.getByText(
                                'order_lookup — success',
                                {
                                    exact:
                                        true,
                                },
                            ),
                        ).toBeVisible();
                    },
                );
            },
        );
    },
);