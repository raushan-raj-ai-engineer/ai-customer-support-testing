import { defineConfig } from '@playwright/test';
import * as os from 'node:os';
import baseConfig from './playwright.config';

export default defineConfig({
  ...baseConfig,

  reporter: [
    ['list'],
    [
      'html',
      {
        outputFolder: 'playwright-report',
        open: 'never',
      },
    ],
    [
      'allure-playwright',
      {
        resultsDir: 'allure-results',
        environmentInfo: {
          project: 'AI Customer Support Testing Platform',
          test_layer: 'Playwright E2E',
          os_platform: os.platform(),
          os_release: os.release(),
          os_version: os.version(),
          node_version: process.version,
          browser: 'Chromium',
          execution: process.env.CI
            ? 'GitHub Actions'
            : 'Local',
        },
      },
    ],
  ],
});
