import {
    defineConfig,
    devices,
} from '@playwright/test';


const baseURL =
    process.env
        .PLAYWRIGHT_BASE_URL ??
    'http://127.0.0.1:4173';


const useExternalServer =
    Boolean(
        process.env
            .PLAYWRIGHT_BASE_URL,
    );


export default defineConfig({
    // ============================================
    // TEST LOCATION
    // ============================================

    testDir:
        './e2e',


    // ============================================
    // EXECUTION
    // ============================================

    fullyParallel:
        true,

    forbidOnly:
        Boolean(
            process.env.CI,
        ),

    retries:
        process.env.CI
            ? 2
            : 0,

    workers:
        process.env.CI
            ? 1
            : undefined,

    timeout:
        30_000,


    // ============================================
    // EXPECT
    // ============================================

    expect: {
        timeout:
            5_000,
    },


    // ============================================
    // REPORTERS
    // ============================================

    reporter: [
        [
            'list',
        ],

        [
            'html',
            {
                outputFolder:
                    'playwright-report',

                open:
                    'never',
            },
        ],
    ],


    // ============================================
    // SHARED BROWSER CONFIGURATION
    // ============================================

    use: {
        baseURL,

        // ------------------------------------------
        // Built-in failure screenshot.
        //
        // Our helper captures every business step.
        // Playwright additionally captures
        // unexpected test failures.
        // ------------------------------------------

        screenshot:
            'only-on-failure',


        // ------------------------------------------
        // Keep trace when a test fails.
        // ------------------------------------------

        trace:
            'retain-on-failure',


        // ------------------------------------------
        // Keep video only for failures.
        // ------------------------------------------

        video:
            'retain-on-failure',
    },


    // ============================================
    // BROWSER
    // ============================================

    projects: [
        {
            name:
                'chromium',

            use: {
                ...devices[
                'Desktop Chrome'
                ],
            },
        },
    ],


    // ============================================
    // LOCAL STATIC UI SERVER
    //
    // Only used when PLAYWRIGHT_BASE_URL
    // is NOT provided.
    // ============================================

    webServer:
        useExternalServer
            ? undefined
            : {
                command:
                    'python3 -m http.server 4173 --bind 127.0.0.1 --directory app/web',

                url:
                    'http://127.0.0.1:4173',

                reuseExistingServer:
                    !process.env.CI,

                timeout:
                    30_000,
            },


    // ============================================
    // OUTPUT
    //
    // Screenshots attached by our helper
    // are saved inside this directory.
    // ============================================

    outputDir:
        'test-results',
});