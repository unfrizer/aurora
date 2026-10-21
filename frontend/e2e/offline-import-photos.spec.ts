import { spawn, type ChildProcess } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { once } from 'node:events';
import { existsSync, mkdirSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { expect, test } from '@playwright/test';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = 'http://127.0.0.1:18766';
const projectsRoot = () => path.join(dataRoot, 'Projects');
const png = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/V9sAAAAASUVORK5CYII=',
  'base64',
);
let server: ChildProcess | null = null;
let dataRoot = '';

interface PersistedState {
  editor: {
    brand: { logo_path: string | null };
    pages: { sections: { image_path: string | null; image_alt: string }[] }[];
  };
}

test.beforeAll(async () => {
  let occupied = false;
  try { await fetch(`${origin}/api/v1/health`); occupied = true; }
  catch { /* The dedicated loopback port is not serving HTTP. */ }
  if (occupied) throw new Error('The import-photo browser test port is already in use');
  const build = path.join(repository, 'build');
  mkdirSync(build, { recursive: true });
  dataRoot = path.join(build, `browser-e2e-${randomUUID()}`);
  server = spawn(path.join(repository, '.venv', 'Scripts', 'python.exe'),
    ['-m', 'tests.browser.server'], {
      cwd: repository,
      env: { ...process.env, AURORA_E2E_ROOT: dataRoot, AURORA_E2E_PORT: '18766' },
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

function onlyProject(): string {
  const names = readdirSync(projectsRoot(), { withFileTypes: true })
    .filter((entry) => entry.isDirectory()).map((entry) => entry.name);
  expect(names).toHaveLength(1);
  return path.join(projectsRoot(), names[0]!);
}

test('prepared JSON and two customer photos survive the offline browser journey', async ({ page }) => {
  const requests: string[] = [];
  const uploads: string[] = [];
  page.on('request', (request) => {
    requests.push(request.url());
    if (request.method() === 'POST' && request.url().endsWith('/assets')) uploads.push(request.url());
  });
  const pageId = randomUUID();
  const sectionId = randomUUID();
  const imported = {
    schema_version: 1,
    language: 'ru',
    brand: { name: 'Мастерская клиента', tagline: 'Работаем вручную',
      primary_color: '#123456', secondary_color: '#abcdef', font_family: 'system', logo_path: null },
    pages: [{ id: pageId, slug: 'index', title: 'Мастерская',
      meta_description: 'Описание мастерской', heading: 'Добро пожаловать',
      sections: [{ id: sectionId, heading: 'Работы', body: 'Описание работ',
        image_path: null, image_alt: 'Фото работ клиента' }] }],
  };
  const logoBytes = Buffer.concat([png, Buffer.from('logo')]);
  const sectionBytes = Buffer.concat([png, Buffer.from('section')]);

  await page.goto(origin);
  await page.getByRole('button', { name: 'Русский' }).click();
  await page.getByRole('button', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Название проекта' }).fill('Клиентский сайт');
  const filePicker = page.getByLabel('JSON-файл подготовленного сайта');
  await filePicker.setInputFiles({ name: 'invalid.json', mimeType: 'application/json', buffer: Buffer.from('{') });
  await page.getByRole('button', { name: 'Импортировать подготовленный сайт' }).click();
  await expect(page.getByText('Файл импорта не содержит корректный JSON.')).toBeVisible();
  if (existsSync(projectsRoot())) expect(readdirSync(projectsRoot())).toHaveLength(0);

  await filePicker.setInputFiles({ name: 'site.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(imported), 'utf8') });
  await page.getByRole('button', { name: 'Импортировать подготовленный сайт' }).click();
  await expect(page.getByRole('heading', { name: 'Клиентский сайт' })).toBeVisible();
  const folder = onlyProject();
  const stored = (): PersistedState =>
    JSON.parse(readFileSync(path.join(folder, 'state.json'), 'utf8')) as PersistedState;
  expect(stored().editor.brand.logo_path).toBeNull();
  expect(stored().editor.pages[0]?.sections[0]?.image_path).toBeNull();

  await page.getByRole('button', { name: 'Фотографии проекта' }).click();
  await page.getByLabel('Выбрать фотографии').setInputFiles([
    { name: 'client-logo.png', mimeType: 'image/png', buffer: logoBytes },
    { name: 'client-work.png', mimeType: 'image/png', buffer: sectionBytes },
  ]);
  const logoRow = page.locator('.photo-tray-item').filter({ hasText: 'client-logo.png' });
  const sectionRow = page.locator('.photo-tray-item').filter({ hasText: 'client-work.png' });
  await expect(logoRow).toBeVisible();
  await expect(sectionRow).toBeVisible();
  const assets = path.join(folder, 'assets');
  if (existsSync(assets)) expect(readdirSync(assets)).toHaveLength(0);
  expect(uploads).toHaveLength(0);
  expect(stored().editor.brand.logo_path).toBeNull();

  await logoRow.getByLabel('Куда прикрепить').selectOption('logo');
  await logoRow.getByRole('button', { name: 'Прикрепить фотографию' }).click();
  await expect(logoRow).toHaveCount(0);
  const logoPath = stored().editor.brand.logo_path;
  expect(logoPath).toMatch(/^assets\/[a-f0-9]{64}\.png$/);
  if (!logoPath) throw new Error('Logo attachment was not saved');
  expect(uploads).toHaveLength(1);
  expect(readFileSync(path.join(folder, logoPath))).toEqual(logoBytes);
  expect(stored().editor.pages[0]?.sections[0]?.image_path).toBeNull();

  await sectionRow.getByLabel('Куда прикрепить').selectOption(`${pageId}/${sectionId}`);
  await sectionRow.getByRole('button', { name: 'Прикрепить фотографию' }).click();
  await expect(sectionRow).toHaveCount(0);
  const section = stored().editor.pages[0]?.sections[0];
  expect(section?.image_path).toMatch(/^assets\/[a-f0-9]{64}\.png$/);
  if (!section?.image_path) throw new Error('Section attachment was not saved');
  expect(uploads).toHaveLength(2);
  expect(section.image_alt).toBe('Фото работ клиента');
  expect(readFileSync(path.join(folder, section.image_path))).toEqual(sectionBytes);

  await page.getByRole('button', { name: 'Предпросмотр' }).click();
  const preview = page.frameLocator('iframe[title="Предпросмотр"]');
  await expect(preview.getByRole('img', { name: 'Фото работ клиента' })).toBeVisible();
  await expect.poll(() => preview.getByRole('img', { name: 'Фото работ клиента' })
    .evaluate((image) => (image as HTMLImageElement).naturalWidth)).toBe(1);

  await page.reload();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await page.getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('heading', { name: 'Клиентский сайт' })).toBeVisible();
  await expect(page.getByRole('img', { name: 'Фото работ клиента' })).toBeVisible();
  expect(stored().editor.brand.logo_path).toBe(logoPath);
  expect(stored().editor.pages[0]?.sections[0]?.image_path).toBe(section.image_path);
  expect(requests.filter((url) => /^https?:/.test(url) && url !== origin &&
    !url.startsWith(`${origin}/`))).toEqual([]);
  expect(requests.filter((url) => /\/(generation|deployments)(\/|$)/.test(url))).toEqual([]);
});
