import { defineConfig, devices } from '@playwright/test';

const origin = 'http://127.0.0.1:18765';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: true,
  retries: 0,
  workers: 1,
  reporter: 'list',
  timeout: 30_000,
  expect: { timeout: 10_000 },
  use: {
    ...devices['Desktop Chrome'],
    channel: 'chrome',
    baseURL: origin,
  },
});
