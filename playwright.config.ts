import {
    defineConfig,
    devices,
} from '@playwright/test';


const baseURL =
    process.env.PLAYWRIGHT_BASE_URL
    ?? 'http://127.0.0.1:4173';


const useStaticServer =
    !process.env.PLAYWRIGHT_BASE_URL;


export default defineConfig({

    testDir: './e2e',

    fullyParallel: true,

    forbidOnly:
        Boolean(
            process.env.CI
        ),

    retries:
        process.env.CI
            ? 2
            : 0,

    workers:
        process.env.CI
            ? 1
            : undefined,

    timeout: 30_000,

    expect: {
        timeout: 5_000,
    },

    reporter: [
        [
            'list',
        ],

        [
            'html',

            {
                open: 'never',
            },
        ],
    ],

    use: {

        baseURL,

        trace:
            'retain-on-failure',

        screenshot:
            'only-on-failure',

        video:
            'retain-on-failure',

        actionTimeout:
            10_000,
    },

    webServer:
        useStaticServer
            ? {
                command:
                    (
                        'python3 -m '
                        + 'http.server 4173 '
                        + '--bind 127.0.0.1 '
                        + '--directory app/web'
                    ),

                url:
                    (
                        'http://127.0.0.1:4173'
                    ),

                reuseExistingServer:
                    !process.env.CI,

                timeout:
                    120_000,
            }
            : undefined,

    projects: [

        {
            name: 'chromium',

            use: {
                ...devices[
                'Desktop Chrome'
                ],
            },
        },

    ],
});