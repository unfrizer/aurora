import { spawn, type ChildProcess } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { once } from 'node:events';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { expect, test } from '@playwright/test';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = 'http://127.0.0.1:18773';
let server: ChildProcess;

test.beforeAll(async () => {
  try { await fetch(`${origin}/api/v1/health`); throw new Error('User controls test port is occupied'); }
  catch (error) { if (error instanceof Error && error.message.includes('occupied')) throw error; }
  server = spawn(path.join(repository, '.venv', 'Scripts', 'python.exe'), ['-m', 'tests.browser.server'], {
    cwd: repository, env: { ...process.env, AURORA_E2E_PORT: '18773',
      AURORA_E2E_ROOT: path.join(repository, 'build', `browser-e2e-${randomUUID()}`) },
    stdio: 'ignore', windowsHide: true,
  });
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (server.exitCode !== null) throw new Error('User controls server exited');
    try { if ((await fetch(`${origin}/api/v1/health`)).ok) return; } catch { /* Wait for startup. */ }
    await delay(100);
  }
  throw new Error('User controls server startup timed out');
});

test.afterAll(async () => {
  if (server && server.exitCode === null) {
    const exited = once(server, 'exit'); server.kill();
    await Promise.race([exited, delay(5000).then(() => { throw new Error('User controls server did not stop'); })]);
  }
});

test.beforeEach(async ({ request }) => {
  const saved = await (await request.get(`${origin}/api/v1/preferences`)).json() as {
    preferences: Record<string, unknown>; revision: string;
  };
  const reset = await request.put(`${origin}/api/v1/preferences`, {
    headers: { Origin: origin, 'X-Aurora-Request': '1' },
    data: { preferences: { ...saved.preferences, language: null, onboarding_completed: false },
      expected_revision: saved.revision },
  });
  expect(reset.ok()).toBe(true);
});

test('first-use errors stay inside the dialog; retry, cross and Escape work', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto(origin);
  const dialog = page.getByRole('dialog', { name: 'AURORA onboarding' });
  const cross = dialog.getByRole('button', { name: 'Закрыть / Close', exact: true });
  await expect(cross).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await expect(dialog.getByRole('button', { name: 'English', exact: true })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(cross).toBeFocused();
  await page.route('**/api/v1/preferences', (route) => route.request().method() === 'PUT'
    ? route.fulfill({ status: 503, contentType: 'application/json', body: '{"error":{"code":503}}' })
    : route.continue());
  await dialog.getByRole('button', { name: 'Русский', exact: true }).click();
  await expect(dialog.getByRole('alert')).toContainText('Не удалось сохранить настройки');
  await dialog.getByRole('button', { name: 'Закрыть / Close', exact: true }).click();
  await expect(dialog.getByRole('alert')).toBeVisible();
  await expect(dialog.getByRole('button', { name: 'Русский', exact: true })).toBeEnabled();
  await page.unroute('**/api/v1/preferences');
  await dialog.getByRole('button', { name: 'Русский', exact: true }).click();
  await dialog.getByRole('button', { name: 'Закрыть', exact: true }).click();
  await expect(dialog).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Проекты', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Инструкция', exact: true }).click();
  await page.route('**/api/v1/preferences', (route) => route.abort());
  await page.keyboard.press('Escape');
  await expect(dialog).toHaveCount(0);
  await page.unroute('**/api/v1/preferences');
  expect(errors).toEqual([]);
});

test('project CRUD, settings, structure, reload and publication cancellation work', async ({ page }) => {
  const errors: string[] = [];
  const paid: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('request', (request) => {
    if (/\/(generation|deployments)(\/|$)/.test(new URL(request.url()).pathname)) paid.push(request.url());
  });
  await page.goto(origin);
  await page.getByRole('button', { name: 'Русский', exact: true }).click();
  await page.getByRole('button', { name: 'Начать', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'AURORA onboarding' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Настройки', exact: true }).click();
  await page.getByRole('combobox', { name: 'Язык интерфейса' }).selectOption('en');
  await page.getByRole('button', { name: 'Сохранить настройки', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  const settingsBox = await page.getByRole('button', { name: 'Settings', exact: true }).boundingBox();
  expect(settingsBox).not.toBeNull();
  expect(settingsBox!.x).toBeGreaterThanOrEqual(0);
  expect(settingsBox!.x + settingsBox!.width).toBeLessThanOrEqual(390);
  await page.getByRole('button', { name: 'Projects', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Projects', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Settings', exact: true }).click();
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.getByRole('checkbox', { name: 'Enable direct AI API requests (billed separately)' }).check();
  const secret = page.locator('.setting-secret').filter({ hasText: 'OpenAI key' });
  await expect(secret.getByRole('button', { name: 'Save key', exact: true })).toBeDisabled();
  await secret.getByRole('textbox').fill('isolated-fake-key');
  await secret.getByRole('button', { name: 'Save key', exact: true }).click();
  await expect(secret.getByText('Connected', { exact: true })).toBeVisible();
  await expect(secret.getByRole('textbox')).toHaveValue('');
  await expect(secret.getByRole('button', { name: 'Save key', exact: true })).toBeDisabled();
  await page.reload();
  await expect(page.getByText('No API charges', { exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Generate with OpenAI' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Settings', exact: true }).click();
  await expect(page.getByRole('checkbox')).not.toBeChecked();
  await expect(page.getByLabel('OpenAI key')).toHaveCount(0);
  await page.getByRole('checkbox', { name: 'Enable direct AI API requests (billed separately)' }).check();
  await expect(secret.getByText('Connected', { exact: true })).toBeVisible();
  await secret.getByRole('button', { name: 'Remove key', exact: true }).click();
  await expect(secret.getByText('Not connected', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Projects', exact: true }).click();
  await page.getByRole('textbox', { name: 'Project name', exact: true }).fill('Controls QA');
  await page.getByRole('button', { name: 'Create project', exact: true }).click();
  await page.getByRole('button', { name: 'Start blank site', exact: true }).click();
  await expect(page.locator('.save-state')).toHaveText('Saved');
  const name = page.getByRole('textbox', { name: 'Project name', exact: true });
  await name.fill('Controls renamed'); await name.press('Tab');
  await expect(page.getByRole('heading', { name: 'Controls renamed', exact: true })).toBeVisible();
  await page.getByRole('textbox', { name: 'Section heading', exact: true }).fill('Second');
  await page.getByRole('button', { name: 'Add section', exact: true }).click();
  await page.getByRole('button', { name: 'Up Second', exact: true }).click();
  await expect(page.locator('.section-card').first().getByRole('textbox', { name: 'Heading', exact: true })).toHaveValue('Second');
  await page.getByRole('button', { name: 'Down Second', exact: true }).click();
  await page.getByRole('textbox', { name: 'Page name', exact: true }).fill('Services');
  await page.getByRole('button', { name: 'Add page', exact: true }).click();
  await page.getByRole('textbox', { name: 'Page name', exact: true }).fill('Contact');
  await page.getByRole('button', { name: 'Add page', exact: true }).click();
  await page.getByRole('button', { name: 'Up Contact', exact: true }).click();
  await expect(page.locator('.page-list .page-select').nth(1)).toHaveText('Contact');
  await page.getByRole('button', { name: 'Down Contact', exact: true }).click();
  await page.getByRole('button', { name: 'Services', exact: true }).click();
  await page.getByRole('button', { name: 'Project photos', exact: true }).click();
  await page.getByRole('region', { name: 'Project photos', exact: true }).getByRole('button', { name: 'Close', exact: true }).click();
  await page.getByRole('button', { name: 'Reload from disk', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Controls renamed', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Export & deploy', exact: true }).click();
  page.once('dialog', (dialog) => void dialog.dismiss());
  await page.getByRole('button', { name: 'Deploy to Netlify', exact: true }).click();
  page.once('dialog', (dialog) => void dialog.dismiss());
  await page.getByRole('button', { name: 'Export site folder', exact: true }).click();
  await page.getByRole('button', { name: 'Projects', exact: true }).click();
  await page.getByRole('searchbox', { name: 'Search projects', exact: true }).fill('no match');
  await expect(page.getByText('No matching projects.')).toBeVisible();
  await page.getByRole('button', { name: 'Clear search', exact: true }).click();
  await page.getByRole('button', { name: 'Delete project', exact: true }).click();
  const remove = page.getByRole('dialog', { name: 'Delete project', exact: true });
  await expect(remove.getByRole('button', { name: 'Delete project', exact: true })).toBeDisabled();
  await remove.getByRole('textbox').fill('Controls renamed');
  await remove.getByRole('button', { name: 'Delete project', exact: true }).click();
  await expect(remove).toHaveCount(0);
  await expect(page.getByText('No projects yet.')).toBeVisible();
  expect(paid).toEqual([]); expect(errors).toEqual([]);
});

test('an exhausted draft quota shows billing guidance without automatic retry', async ({ page }) => {
  let attempts = 0;
  await page.route('**/api/v1/projects/*/generation/draft', async (route) => {
    attempts += 1;
    const request = route.request().postDataJSON() as { expected_updated_at: string };
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({
      job_id: randomUUID(), status: 'failed', source_updated_at: request.expected_updated_at,
      editor: null, failure: { category: 'rate_limited', retryable: false, message: 'PRIVATE_PROVIDER_BODY' },
    }) });
  });
  await page.goto(origin);
  await page.getByRole('button', { name: 'Русский', exact: true }).click();
  await page.getByRole('button', { name: 'Начать', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'AURORA onboarding' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Настройки', exact: true }).click();
  await page.getByRole('checkbox', { name: 'Включить прямые AI-запросы через API (оплачиваются отдельно)' }).check();
  await page.getByRole('button', { name: 'Проекты', exact: true }).click();
  await page.getByRole('textbox', { name: 'Название проекта', exact: true }).fill('Quota guidance QA');
  await page.getByRole('textbox', { name: 'Опишите бизнес одним запросом' }).fill('Сайт мастерской');
  page.once('dialog', (dialog) => void dialog.accept());
  await page.getByRole('button', { name: 'Создать из запроса', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('API-кредитов или квоты');
  await expect(page.getByRole('link', { name: 'Баланс API OpenAI' })).toHaveAttribute('target', '_blank');
  await expect(page.getByRole('link', { name: 'Лимиты OpenAI' })).toBeVisible();
  await expect(page.getByText('PRIVATE_PROVIDER_BODY')).toHaveCount(0);
  await expect(page.getByRole('textbox', { name: 'Опишите бизнес одним запросом' })).toHaveValue('Сайт мастерской');
  await page.getByRole('button', { name: 'Проекты', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Quota guidance QA', exact: true })).toBeVisible();
  expect(attempts).toBe(1);
});
