import { spawn, type ChildProcess } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { once } from 'node:events';
import { existsSync, mkdirSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { expect, test } from '@playwright/test';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = 'http://127.0.0.1:18771';
const projectsRoot = () => path.join(dataRoot, 'Projects');
let server: ChildProcess | null = null;
let dataRoot = '';

interface PersistedState {
  editor: {
    schema_version: number;
    language: string;
    brand: { name: string; tagline: string; logo_path: string | null };
    pages: {
      slug: string;
      meta_description: string;
      sections: { body: string; image_path: string | null }[];
    }[];
  };
}

test.beforeAll(async () => {
  let occupied = false;
  try { await fetch(`${origin}/api/v1/health`); occupied = true; }
  catch { /* The dedicated loopback port is not serving HTTP. */ }
  if (occupied) throw new Error('The offline brief browser test port is already in use');
  const build = path.join(repository, 'build');
  mkdirSync(build, { recursive: true });
  dataRoot = path.join(build, `browser-e2e-${randomUUID()}`);
  server = spawn(path.join(repository, '.venv', 'Scripts', 'python.exe'),
    ['-m', 'tests.browser.server'], {
      cwd: repository,
      env: { ...process.env, AURORA_E2E_ROOT: dataRoot, AURORA_E2E_PORT: '18771' },
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

test('offline brief requires public-content consent and survives preview, export and reopen', async ({ page }) => {
  const requests: { method: string; url: string; body: string | null }[] = [];
  page.on('request', (request) => requests.push({
    method: request.method(), url: request.url(), body: request.postData(),
  }));
  const brief = '  Ремонт велосипедов\nДиагностика и настройка  ';

  await page.goto(origin);
  await page.getByRole('button', { name: 'Русский' }).click();
  await page.getByRole('button', { name: 'Начать' }).click();
  const name = page.getByRole('textbox', { name: 'Название проекта' });
  await name.fill('Веломастерская');
  await page.getByRole('textbox', { name: 'ТЗ для офлайн-старта' }).fill(brief);
  await expect(page.getByText(/Это не приватная заметка/)).toBeVisible();
  await name.press('Enter');
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  expect(requests.filter((request) => request.method === 'POST' &&
    request.url === `${origin}/api/v1/projects`)).toHaveLength(0);

  let publicWarning = '';
  page.once('dialog', (dialog) => { publicWarning = dialog.message(); void dialog.dismiss(); });
  await page.getByRole('button', { name: 'Создать проект с ТЗ' }).click();
  expect(publicWarning).toContain('ТЗ будет без изменений видно на сайте');
  expect(requests.filter((request) => request.method === 'POST' &&
    request.url === `${origin}/api/v1/projects`)).toHaveLength(0);
  expect(requests.filter((request) => request.method === 'PUT' &&
    /\/projects\/[^/]+\/editor$/.test(new URL(request.url).pathname))).toHaveLength(0);
  if (existsSync(projectsRoot())) expect(readdirSync(projectsRoot())).toHaveLength(0);

  const createdResponse = page.waitForResponse((response) =>
    response.url() === `${origin}/api/v1/projects` && response.request().method() === 'POST');
  page.once('dialog', (dialog) => void dialog.accept());
  await page.getByRole('button', { name: 'Создать проект с ТЗ' }).click();
  const created = await (await createdResponse).json() as {
    metadata: { project_id: string; updated_at: string };
  };
  await expect(page.getByRole('heading', { name: 'Веломастерская' })).toBeVisible();
  const names = readdirSync(projectsRoot(), { withFileTypes: true })
    .filter((entry) => entry.isDirectory()).map((entry) => entry.name);
  expect(names).toHaveLength(1);
  const folder = path.join(projectsRoot(), names[0]!);
  const stored = (): PersistedState =>
    JSON.parse(readFileSync(path.join(folder, 'state.json'), 'utf8')) as PersistedState;
  expect(stored().editor).toMatchObject({
    schema_version: 1, language: 'ru',
    brand: { name: 'Веломастерская', tagline: '', logo_path: null },
    pages: [{ slug: 'index', meta_description: '',
      sections: [{ body: brief, image_path: null }] }],
  });
  expect(stored().editor.pages).toHaveLength(1);
  expect(stored().editor.pages[0]?.sections).toHaveLength(1);
  const creates = requests.filter((request) => request.method === 'POST' &&
    request.url === `${origin}/api/v1/projects`);
  const saves = requests.filter((request) => request.method === 'PUT' &&
    /^\/api\/v1\/projects\/[^/]+\/editor$/.test(new URL(request.url).pathname));
  expect(creates).toHaveLength(1);
  expect(saves).toHaveLength(1);
  expect(JSON.parse(saves[0]?.body ?? '{}') as { expected_updated_at?: unknown })
    .toMatchObject({ expected_updated_at: created.metadata.updated_at });
  expect(new URL(saves[0]!.url).pathname)
    .toBe(`/api/v1/projects/${created.metadata.project_id}/editor`);

  await page.getByRole('button', { name: 'Предпросмотр' }).click();
  const preview = page.frameLocator('iframe[title="Предпросмотр"]');
  await expect(preview.getByText(/Ремонт велосипедов/)).toBeVisible();
  await expect(preview.getByText(/Диагностика и настройка/)).toBeVisible();
  await page.getByRole('button', { name: 'Экспорт и деплой' }).click();
  page.once('dialog', (dialog) => void dialog.accept());
  await page.getByRole('button', { name: 'Экспортировать папку сайта' }).click();
  const exportPath = await page.getByRole('textbox', { name: 'Папка готового сайта' }).inputValue();
  expect(path.resolve(path.dirname(exportPath))).toBe(path.resolve(folder, 'exports'));
  const html = readFileSync(path.join(exportPath, 'index.html'), 'utf8');
  expect(html).toContain('Ремонт велосипедов');
  expect(html).toContain('Диагностика и настройка');

  await page.reload();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await page.getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('heading', { name: 'Веломастерская' })).toBeVisible();
  await expect(page.getByRole('textbox', { name: 'Текст' })).toHaveValue(brief);
  expect(stored().editor.pages[0]?.sections[0]?.body).toBe(brief);
  expect(requests.filter((request) => /^https?:/.test(request.url) && request.url !== origin &&
    !request.url.startsWith(`${origin}/`))).toEqual([]);
  expect(requests.filter((request) => {
    const pathname = new URL(request.url).pathname;
    return /\/(generation|deployments|credentials)(\/|$)/.test(pathname) ||
      ((request.method === 'POST' || request.method === 'DELETE') && /\/assets(\/|$)/.test(pathname));
  })).toEqual([]);
});
