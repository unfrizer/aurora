import { spawn, type ChildProcess } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { once } from 'node:events';
import { mkdirSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { expect, test } from '@playwright/test';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = 'http://127.0.0.1:18772';
let server: ChildProcess | null = null;
let dataRoot = '';

test.beforeAll(async () => {
  let occupied = false;
  try { await fetch(`${origin}/api/v1/health`); occupied = true; }
  catch { /* The dedicated loopback port is not serving HTTP. */ }
  if (occupied) throw new Error('The manual site browser test port is already in use');
  mkdirSync(path.join(repository, 'build'), { recursive: true });
  dataRoot = path.join(repository, 'build', `browser-e2e-${randomUUID()}`);
  server = spawn(path.join(repository, '.venv', 'Scripts', 'python.exe'),
    ['-m', 'tests.browser.server'], {
      cwd: repository,
      env: { ...process.env, AURORA_E2E_ROOT: dataRoot, AURORA_E2E_PORT: '18772' },
      stdio: 'ignore', windowsHide: true,
    });
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (server.exitCode !== null) throw new Error('Isolated browser test server exited early');
    try {
      const response = await fetch(`${origin}/api/v1/health`);
      if (response.ok) return;
    } catch { /* Wait for local server startup. */ }
    await delay(100);
  }
  throw new Error('Isolated browser test server did not become ready');
});

test.afterAll(async () => {
  if (server && server.exitCode === null) {
    const exited = once(server, 'exit');
    if (!server.kill()) throw new Error('Could not stop isolated browser test server');
    await Promise.race([exited, delay(5_000).then(() => {
      throw new Error('Isolated browser test server did not stop');
    })]);
  }
});

test('manual public copy is saved, previewed, exported and reopened without AI', async ({ page }) => {
  const requests: { method: string; url: string }[] = [];
  page.on('request', (request) => requests.push({ method: request.method(), url: request.url() }));
  await page.goto(origin);
  await page.getByRole('button', { name: 'Русский' }).click();
  await page.getByRole('button', { name: 'Начать' }).click();
  await page.getByRole('textbox', { name: 'Название проекта' }).fill('Велостудия');
  await page.getByText('Собрать сайт из моих текстов').click();
  await page.getByRole('textbox', { name: 'Слоган для сайта (необязательно)' }).fill('Ваш велосипед в порядке');
  await page.getByRole('textbox', { name: 'Главный заголовок сайта' }).fill('Ремонт велосипедов');
  await page.getByRole('textbox', { name: 'Заголовок первого раздела' }).fill('Наши услуги');
  await page.getByRole('textbox', { name: 'Текст первого раздела' }).fill('Диагностика и настройка');
  await page.getByRole('textbox', { name: 'SEO-описание (необязательно)' }).fill('Мастерская велосипедов');
  let warning = '';
  page.once('dialog', (dialog) => { warning = dialog.message(); void dialog.dismiss(); });
  await page.getByRole('button', { name: 'Создать сайт из моих текстов' }).click();
  expect(warning).toContain('будут видны на сайте');
  expect(requests.filter((request) => request.method === 'POST' &&
    request.url === `${origin}/api/v1/projects`)).toHaveLength(0);

  const createdResponse = page.waitForResponse((response) =>
    response.url() === `${origin}/api/v1/projects` && response.request().method() === 'POST');
  page.once('dialog', (dialog) => void dialog.accept());
  await page.getByRole('button', { name: 'Создать сайт из моих текстов' }).click();
  const created = await (await createdResponse).json() as {
    metadata: { project_id: string; updated_at: string };
  };
  await expect(page.getByRole('heading', { name: 'Велостудия' })).toBeVisible();
  const projectDirectories = readdirSync(path.join(dataRoot, 'Projects'), { withFileTypes: true })
    .filter((entry) => entry.isDirectory()).map((entry) => entry.name);
  expect(projectDirectories).toHaveLength(1);
  const projectFolder = path.join(dataRoot, 'Projects', projectDirectories[0]!);
  const state = JSON.parse(readFileSync(path.join(projectFolder, 'state.json'), 'utf8')) as {
    editor: { brand: { tagline: string; primary_color: string; secondary_color: string; font_family: string };
      pages: { heading: string; meta_description: string;
      sections: { heading: string; body: string }[] }[] };
  };
  expect(state.editor).toMatchObject({ brand: { tagline: 'Ваш велосипед в порядке' },
    pages: [{ heading: 'Ремонт велосипедов', meta_description: 'Мастерская велосипедов',
      sections: [{ heading: 'Наши услуги', body: 'Диагностика и настройка' }] }] });
  const saves = requests.filter((request) => request.method === 'PUT' &&
    /^\/api\/v1\/projects\/[^/]+\/editor$/.test(new URL(request.url).pathname));
  expect(saves).toHaveLength(1);
  expect(new URL(saves[0]!.url).pathname).toBe(`/api/v1/projects/${created.metadata.project_id}/editor`);

  const preset = page.getByRole('combobox', { name: 'Готовое оформление' });
  await preset.selectOption('forest');
  expect(requests.filter((request) => request.method === 'PUT' &&
    /^\/api\/v1\/projects\/[^/]+\/editor$/.test(new URL(request.url).pathname))).toHaveLength(1);
  const styleSave = page.waitForResponse((response) => response.request().method() === 'PUT' &&
    new URL(response.url()).pathname === `/api/v1/projects/${created.metadata.project_id}/editor`);
  await page.getByRole('button', { name: 'Применить оформление' }).click();
  expect((await styleSave).ok()).toBe(true);
  const styled = JSON.parse(readFileSync(path.join(projectFolder, 'state.json'), 'utf8')) as typeof state;
  expect(styled.editor.brand).toMatchObject({ tagline: 'Ваш велосипед в порядке',
    primary_color: '#166534', secondary_color: '#14532D', font_family: 'serif' });
  expect(styled.editor.pages).toEqual(state.editor.pages);

  await page.getByRole('button', { name: 'Предпросмотр' }).click();
  await expect(page.frameLocator('iframe[title="Предпросмотр"]').getByText('Диагностика и настройка')).toBeVisible();
  await page.getByRole('button', { name: 'Экспорт и деплой' }).click();
  page.once('dialog', (dialog) => void dialog.accept());
  await page.getByRole('button', { name: 'Экспортировать папку сайта' }).click();
  const exportPath = await page.getByRole('textbox', { name: 'Папка готового сайта' }).inputValue();
  const html = readFileSync(path.join(exportPath, 'index.html'), 'utf8');
  expect(html).toContain('Ремонт велосипедов');
  expect(html).toContain('Диагностика и настройка');
  const css = readFileSync(path.join(exportPath, 'assets', 'site.css'), 'utf8');
  expect(css).toContain('--primary: #166534');
  expect(css).toContain('--secondary: #14532D');
  expect(css).toContain('font-family: Georgia, serif');
  await page.reload();
  await page.getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('textbox', { name: 'Текст' })).toHaveValue('Диагностика и настройка');
  await expect(page.getByRole('textbox', { name: 'Основной цвет' })).toHaveValue('#166534');
  expect(requests.filter((request) => /\/(generation|deployments|credentials)(\/|$)/
    .test(new URL(request.url).pathname))).toEqual([]);
});
