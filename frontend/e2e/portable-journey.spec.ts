import { statSync } from 'node:fs';
import { expect, test } from '@playwright/test';

const origin = process.env.AURORA_PORTABLE_ORIGIN;

test('packaged Windows UI can edit, preview, export and reopen a blank site', async ({ page }) => {
  test.skip(!origin, 'Only the isolated portable Windows smoke supplies an origin');
  if (!origin || !/^http:\/\/127\.0\.0\.1:\d+$/.test(origin)) {
    throw new Error('Expected the packaged executable loopback origin');
  }

  const unexpectedRequests: string[] = [];
  page.on('request', (request) => {
    const url = request.url();
    if (/^https?:/.test(url) && url !== origin && !url.startsWith(`${origin}/`)) {
      unexpectedRequests.push(url);
    }
    if (request.method() === 'POST' && /\/(generation|deployments)(\/|$)/.test(url)) {
      unexpectedRequests.push(url);
    }
  });

  await page.goto(origin);
  await page.getByRole('button', { name: 'Русский' }).click();
  await page.getByRole('button', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await expect(page.locator('.project-card')).toHaveCount(1);
  await page.getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('heading', { name: 'Packaged Smoke' })).toBeVisible();
  await page.getByRole('button', { name: 'Начать с пустого сайта' }).click();

  const body = page.getByRole('textbox', { name: 'Текст' });
  await expect(body).toBeVisible();
  await body.fill('Текст из проверенной portable-сборки.');
  await body.press('Tab');
  await page.getByRole('button', { name: 'Сохранить', exact: true }).click();
  await page.getByRole('button', { name: 'Предпросмотр' }).click();
  await expect(page.frameLocator('iframe[title="Предпросмотр"]')
    .getByText('Текст из проверенной portable-сборки.')).toBeVisible();

  await page.getByRole('button', { name: 'Экспорт и деплой' }).click();
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Скачать ZIP сайта' }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('aurora-site.zip');
  expect(statSync(await download.path()).size).toBeGreaterThan(0);

  await page.reload();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await expect(page.getByRole('dialog', { name: 'AURORA onboarding' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('textbox', { name: 'Текст' }))
    .toHaveValue('Текст из проверенной portable-сборки.');
  expect(unexpectedRequests).toEqual([]);
});
