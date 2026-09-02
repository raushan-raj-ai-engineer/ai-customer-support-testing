import {
    expect,
    test,
} from '@playwright/test';


const runLive =
    process.env.RUN_LIVE_BACKEND_E2E
    === '1';


test.describe(
    'Live secure backend',
    () => {

        test.skip(
            !runLive,

            (
                'Set RUN_LIVE_BACKEND_E2E=1 '
                + 'and point PLAYWRIGHT_BASE_URL '
                + 'to the running FastAPI app.'
            ),
        );


        test(
            'real order lookup works end-to-end',

            async ({
                page,
            }) => {

                const uiPath =
                    process.env
                        .PLAYWRIGHT_UI_PATH
                    ?? '/support';


                await page.goto(
                    uiPath,
                );


                await page
                    .getByLabel(
                        'Your question',
                    )
                    .fill(
                        'Where is ORD-1001?',
                    );


                await page
                    .getByRole(
                        'button',

                        {
                            name:
                                'Ask support agent',
                        },
                    )
                    .click();


                await expect(
                    page.getByText(
                        /ORD-1001/,
                    ),
                ).toBeVisible();


                await expect(
                    page.getByText(
                        /SHIPPED/,
                    ),
                ).toBeVisible();


                await expect(
                    page.getByText(
                        'Allowed',
                    ),
                ).toBeVisible();


                await expect(
                    page.getByText(
                        'order_lookup — success',
                    ),
                ).toBeVisible();
            },
        );
    },
);