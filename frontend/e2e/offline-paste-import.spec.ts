import { spawn, type ChildProcess } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { once } from 'node:events';
import { existsSync, mkdirSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { expect, test } from '@playwright/test';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = 'http://127.0.0.1:18768';
const projectsRoot = () => path.join(dataRoot, 'Projects');
let server: ChildProcess | null = null;
let dataRoot = '';

test.beforeAll(async () => {
  let occupied = false;
  try { await fetch(`${origin}/api/v1/health`); occupied = true; }
  catch { /* The dedicated loopback port is not serving HTTP. */ }
  if (occupied) throw new Error('The paste-import browser test port is already in use');
  const build = path.join(repository, 'build');
  mkdirSync(build, { recursive: true });
  dataRoot = path.join(build, `browser-e2e-${randomUUID()}`);
  server = spawn(path.join(repository, '.venv', 'Scripts', 'python.exe'),
    ['-m', 'tests.browser.server'], {
      cwd: repository,
      env: { ...process.env, AURORA_E2E_ROOT: dataRoot, AURORA_E2E_PORT: '18768' },
      stdio: 'ignore',
      windowsHide: true,
    });
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (server.exitCode !== null) throw new Error('Isolated browser test server exited early');
    try {
      const response = await fetch(`${origin}/api/v1/health`);
      if (response.ok) return;
    } catch { /* Wait for the local server to bind. */ }
    await delay(100);
  }
  throw new Error('Isolated browser test server did not become ready');
});

test.afterAll(async () => {
  if (server && server.exitCode === null) {
    const exited = once(server, 'exit');
    if (!server.kill()) throw new Error('Could not stop isolated browser test server');
    await Promise.race([
      exited,
      delay(5_000).then(() => { throw new Error('Isolated browser test server did not stop'); }),
    ]);
  }
});

test('pasted P7 JSON creates, previews and reopens one offline project', async ({ page }) => {
  const requests: { method: string; url: string }[] = [];
  page.on('request', (request) => requests.push({ method: request.method(), url: request.url() }));
  const imported = {
    schema_version: 1,
    language: 'ru',
    brand: { name: 'Мастерская из текста', tagline: 'Готовый проект',
      primary_color: '#123456', secondary_color: '#abcdef', font_family: 'system', logo_path: null },
    pages: [{ id: randomUUID(), slug: 'index', title: 'Мастерская из текста',
      meta_description: 'Описание проекта', heading: 'Добро пожаловать',
      sections: [{ id: randomUUID(), heading: 'О нас', body: 'Сайт из подготовленного JSON',
        image_path: null, image_alt: '' }] }],
  };

  await page.goto(origin);
  await page.getByRole('button', { name: 'Русский' }).click();
  await page.getByRole('button', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Название проекта' }).fill('Сайт из вставки');
  const paste = page.getByRole('textbox', { name: 'Вставьте JSON подготовленного сайта' });
  await paste.fill('{');
  await page.getByRole('textbox', { name: 'Название проекта' }).press('Enter');
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  expect(requests.filter((request) => request.method === 'POST' &&
    request.url === `${origin}/api/v1/projects`)).toHaveLength(0);
  if (existsSync(projectsRoot())) expect(readdirSync(projectsRoot())).toHaveLength(0);
  await page.getByRole('button', { name: 'Импортировать вставленный сайт' }).click();
  await expect(page.getByText('Файл импорта не содержит корректный JSON.')).toBeVisible();
  if (existsSync(projectsRoot())) expect(readdirSync(projectsRoot())).toHaveLength(0);
  expect(requests.filter((request) => request.method === 'POST' &&
    request.url === `${origin}/api/v1/projects`)).toHaveLength(0);

  await page.getByLabel('JSON-файл подготовленного сайта').setInputFiles({
    name: 'invalid.json', mimeType: 'application/json', buffer: Buffer.from('{'),
  });
  await paste.fill(JSON.stringify(imported));
  await page.getByRole('button', { name: 'Импортировать вставленный сайт' }).click();
  await expect(page.getByRole('heading', { name: 'Сайт из вставки' })).toBeVisible();
  const names = readdirSync(projectsRoot(), { withFileTypes: true })
    .filter((entry) => entry.isDirectory()).map((entry) => entry.name);
  expect(names).toHaveLength(1);
  const folder = path.join(projectsRoot(), names[0]!);
  const saved = JSON.parse(readFileSync(path.join(folder, 'state.json'), 'utf8')) as { editor: unknown };
  expect(saved.editor).toEqual(imported);
  expect(requests.filter((request) => request.method === 'POST' &&
    request.url === `${origin}/api/v1/projects`)).toHaveLength(1);
  expect(requests.filter((request) => request.method === 'PUT' &&
    /^\/api\/v1\/projects\/[^/]+\/editor$/.test(new URL(request.url).pathname))).toHaveLength(1);

  await page.getByRole('button', { name: 'Предпросмотр' }).click();
  const preview = page.frameLocator('iframe[title="Предпросмотр"]');
  await expect(preview.getByRole('heading', { name: 'Добро пожаловать' })).toBeVisible();
  await expect(preview.getByText('Сайт из подготовленного JSON')).toBeVisible();

  await page.reload();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await page.getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('heading', { name: 'Сайт из вставки' })).toBeVisible();
  expect((JSON.parse(readFileSync(path.join(folder, 'state.json'), 'utf8')) as { editor: unknown }).editor)
    .toEqual(imported);
  expect(requests.filter((request) => /^https?:/.test(request.url) && request.url !== origin &&
    !request.url.startsWith(`${origin}/`))).toEqual([]);
  expect(requests.filter((request) => {
    const pathname = new URL(request.url).pathname;
    return /\/(generation|deployments)(\/|$)/.test(pathname) ||
      ((request.method === 'POST' || request.method === 'DELETE') && /\/assets(\/|$)/.test(pathname));
  })).toEqual([]);
});
