import {
    expect,
    test,
} from '@playwright/test';


test.describe(
    'AI Support UI',
    () => {

        test(
            'renders accessible support form',

            async ({
                page,
            }) => {

                await page.goto('/');

                await expect(
                    page.getByRole(
                        'heading',

                        {
                            name:
                                'AI Customer Support',
                        },
                    ),
                ).toBeVisible();

                await expect(
                    page.getByLabel(
                        'Your question',
                    ),
                ).toBeVisible();

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


        test(
            'submits shipping question and displays agent result',

            async ({
                page,
            }) => {

                let submittedBody:
                    unknown = null;


                await page.route(
                    '**/api/v1/secure-agent/chat',

                    async (
                        route,
                    ) => {

                        submittedBody =
                            route
                                .request()
                                .postDataJSON();

                        await route.fulfill({

                            status: 200,

                            contentType:
                                'application/json',

                            body:
                                JSON.stringify(
                                    {
                                        message:
                                            (
                                                'How long does '
                                                + 'standard shipping '
                                                + 'take?'
                                            ),

                                        intent:
                                            'policy',

                                        answer:
                                            (
                                                'Standard shipping '
                                                + 'normally takes '
                                                + '3 to 5 business days.'
                                            ),

                                        tool_calls: [
                                            {
                                                name:
                                                    'rag_policy_lookup',

                                                input: {
                                                    question:
                                                        (
                                                            'How long does '
                                                            + 'standard shipping '
                                                            + 'take?'
                                                        ),
                                                },

                                                success:
                                                    true,

                                                output: {
                                                    retrieved_policy_ids:
                                                        [
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
                                    },
                                ),
                        });
                    },
                );


                await page.goto('/');


                await page
                    .getByLabel(
                        'Your question',
                    )
                    .fill(
                        (
                            'How long does '
                            + 'standard shipping '
                            + 'take?'
                        ),
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
                        (
                            'Standard shipping '
                            + 'normally takes '
                            + '3 to 5 business days.'
                        ),
                    ),
                ).toBeVisible();


                await expect(
                    page.getByText(
                        'policy',
                        {
                            exact: true,
                        },
                    ),
                ).toBeVisible();


                await expect(
                    page.getByText(
                        'Allowed',
                    ),
                ).toBeVisible();


                expect(
                    submittedBody,
                ).toEqual(
                    {
                        message:
                            (
                                'How long does '
                                + 'standard shipping '
                                + 'take?'
                            ),

                        approve_write:
                            false,
                    },
                );
            },
        );


        test(
            'example button populates question',

            async ({
                page,
            }) => {

                await page.goto('/');

                await page
                    .getByRole(
                        'button',

                        {
                            name:
                                'Track ORD-1001',
                        },
                    )
                    .click();

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