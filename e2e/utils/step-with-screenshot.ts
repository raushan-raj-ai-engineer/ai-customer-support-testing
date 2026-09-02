import {
    Page,
    TestInfo,
    test,
} from '@playwright/test';


type StepAction =
    () => Promise<void>;


/**
 * Converts a readable step name into a safe
 * screenshot filename.
 *
 * Example:
 *
 * "01 Open support page"
 *
 * becomes:
 *
 * "01-open-support-page"
 */
function sanitizeFileName(
    value: string,
): string {
    return value
        .trim()
        .toLowerCase()
        .replace(
            /[^a-z0-9]+/g,
            '-',
        )
        .replace(
            /^-+|-+$/g,
            '',
        );
}


/**
 * Executes one meaningful Playwright business step.
 *
 * On PASS:
 * - screenshot is captured
 * - screenshot is attached to HTML report
 *
 * On FAILURE:
 * - FAILED screenshot is captured
 * - screenshot is attached
 * - original error is thrown again
 *
 * Throwing the original error is important:
 * screenshot capture must never make a failed test pass.
 */
export async function stepWithScreenshot(
    page: Page,
    testInfo: TestInfo,
    stepName: string,
    action: StepAction,
): Promise<void> {
    await test.step(
        stepName,
        async () => {
            const safeName =
                sanitizeFileName(
                    stepName,
                );

            try {
                // -----------------------------
                // Execute actual test step
                // -----------------------------

                await action();


                // -----------------------------
                // PASS screenshot
                // -----------------------------

                const screenshotPath =
                    testInfo.outputPath(
                        `${safeName}.png`,
                    );

                await page.screenshot({
                    path: screenshotPath,
                    fullPage: true,
                });


                // -----------------------------
                // Attach screenshot
                // to Playwright HTML report
                // -----------------------------

                await testInfo.attach(
                    `${stepName} - Screenshot`,
                    {
                        path: screenshotPath,
                        contentType:
                            'image/png',
                    },
                );
            } catch (error) {
                // -----------------------------
                // FAILURE screenshot
                // -----------------------------

                const failurePath =
                    testInfo.outputPath(
                        `${safeName}-FAILED.png`,
                    );

                try {
                    await page.screenshot({
                        path: failurePath,
                        fullPage: true,
                    });

                    await testInfo.attach(
                        `${stepName} - FAILED`,
                        {
                            path: failurePath,
                            contentType:
                                'image/png',
                        },
                    );
                } catch (
                screenshotError
                ) {
                    console.error(
                        'Unable to capture failure screenshot:',
                        screenshotError,
                    );
                }


                // -----------------------------
                // IMPORTANT
                //
                // Re-throw original Playwright
                // assertion/action error.
                // -----------------------------

                throw error;
            }
        },
    );
}