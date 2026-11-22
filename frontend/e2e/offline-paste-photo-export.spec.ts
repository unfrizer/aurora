import { spawn, type ChildProcess, execFileSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import { once } from 'node:events';
import { existsSync, mkdirSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { expect, test } from '@playwright/test';
import { preparedSitePromptWithBrief } from '../src/prepared_site_prompt';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = 'http://127.0.0.1:18770';
const projectsRoot = () => path.join(dataRoot, 'Projects');
const png = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/V9sAAAAASUVORK5CYII=',
  'base64',
);
let server: ChildProcess | null = null;
let dataRoot = '';

interface PersistedState {
  editor: { pages: { sections: { image_path: string | null; image_alt: string }[] }[] };
}

test.beforeAll(async () => {
  let occupied = false;
  try { await fetch(`${origin}/api/v1/health`); occupied = true; }
  catch { /* The dedicated loopback port is not serving HTTP. */ }
  if (occupied) throw new Error('The paste-export browser test port is already in use');
  const build = path.join(repository, 'build');
  mkdirSync(build, { recursive: true });
  dataRoot = path.join(build, `browser-e2e-${randomUUID()}`);
  server = spawn(path.join(repository, '.venv', 'Scripts', 'python.exe'),
    ['-m', 'tests.browser.server'], {
      cwd: repository,
      env: { ...process.env, AURORA_E2E_ROOT: dataRoot, AURORA_E2E_PORT: '18770' },
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

test('ChatGPT brief transfer, fenced response, editing and photos export without API calls', async ({ page }) => {
  const requests: { method: string; url: string }[] = [];
  const errors: string[] = [];
  const copied: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.exposeFunction('captureCopiedPrompt', (value: string) => { copied.push(value); });
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: {
      writeText: (value: string) => (window as unknown as { captureCopiedPrompt: (text: string) => Promise<void> }).captureCopiedPrompt(value),
    } });
  });
  page.on('request', (request) => requests.push({ method: request.method(), url: request.url() }));
  const pageId = randomUUID();
  const sectionId = randomUUID();
  const imported = {
    schema_version: 1, language: 'ru',
    brand: { name: 'Мастерская клиента', tagline: 'Работаем вручную',
      primary_color: '#123456', secondary_color: '#abcdef', font_family: 'system', logo_path: null },
    pages: [{ id: pageId, slug: 'index', title: 'Мастерская клиента',
      meta_description: 'Услуги мастерской клиента', heading: 'Добро пожаловать',
      sections: [{ id: sectionId, heading: 'Работы', body: 'Текст из подготовленного JSON',
        image_path: null, image_alt: 'Работа клиента' }] }],
  };
  const photoBytes = Buffer.concat([png, Buffer.from('offline-export-photo')]);

  await page.goto(origin);
  await page.getByRole('button', { name: 'Русский' }).click();
  await page.getByRole('button', { name: 'Начать' }).click();
  await expect(page.getByRole('dialog', { name: 'AURORA onboarding' })).toHaveCount(0);
  await expect(page.getByRole('region', { name: 'Создать с OpenAI' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Настройки', exact: true }).click();
  await expect(page.getByRole('checkbox')).not.toBeChecked();
  await expect(page.getByLabel('Ключ OpenAI')).toHaveCount(0);
  await page.getByRole('button', { name: 'Проекты', exact: true }).click();
  const brief = 'Сайт мастерской: услуги, примеры работ и контакты. Тексты на русском.';
  await page.getByRole('textbox', { name: 'ТЗ для внешней подготовки', exact: true }).fill(brief);
  await page.getByRole('button', { name: 'Копировать шаблон с ТЗ', exact: true }).click();
  await expect(page.getByRole('status')).toHaveText('Шаблон с ТЗ скопирован.');
  expect(copied).toEqual([preparedSitePromptWithBrief('ru', brief)]);
  await expect(page.getByRole('link', { name: 'Открыть ChatGPT', exact: true })).toHaveAttribute('href', 'https://chatgpt.com/');
  await page.getByRole('textbox', { name: 'Название проекта' }).fill('Сайт для экспорта');
  await page.getByRole('textbox', { name: 'Вставьте JSON подготовленного сайта' })
    .fill(`\`\`\`json\n${JSON.stringify(imported, null, 2)}\n\`\`\``);
  await page.getByRole('button', { name: 'Импортировать вставленный сайт' }).click();
  await expect(page.getByRole('heading', { name: 'Сайт для экспорта' })).toBeVisible();
  const names = readdirSync(projectsRoot(), { withFileTypes: true })
    .filter((entry) => entry.isDirectory()).map((entry) => entry.name);
  expect(names).toHaveLength(1);
  const projectFolder = path.join(projectsRoot(), names[0]!);
  const stored = (): PersistedState =>
    JSON.parse(readFileSync(path.join(projectFolder, 'state.json'), 'utf8')) as PersistedState;
  expect(stored().editor.pages[0]?.sections[0]?.image_path).toBeNull();
  await expect(page.getByRole('button', { name: 'Сгенерировать изображение', exact: true })).toHaveCount(0);
  const body = page.getByRole('textbox', { name: 'Текст', exact: true });
  await body.fill('Текст клиента, отредактированный без API');
  await body.blur();
  await expect(page.getByText('Сохранено', { exact: true }).first()).toBeVisible();

  await page.getByRole('button', { name: 'Фотографии проекта' }).click();
  await page.getByLabel('Выбрать фотографии').setInputFiles({
    name: 'client-work.png', mimeType: 'image/png', buffer: photoBytes,
  });
  const photoRow = page.locator('.photo-tray-item').filter({ hasText: 'client-work.png' });
  await expect(photoRow).toBeVisible();
  expect(requests.filter((request) => request.method === 'POST' && request.url.endsWith('/assets')))
    .toHaveLength(0);
  const assets = path.join(projectFolder, 'assets');
  if (existsSync(assets)) expect(readdirSync(assets)).toHaveLength(0);
  await photoRow.getByLabel('Куда прикрепить').selectOption(`${pageId}/${sectionId}`);
  await photoRow.getByRole('button', { name: 'Прикрепить фотографию' }).click();
  await expect(photoRow).toHaveCount(0);
  const section = stored().editor.pages[0]?.sections[0];
  expect(section?.image_path).toMatch(/^assets\/[a-f0-9]{64}\.png$/);
  expect(section?.image_alt).toBe('Работа клиента');
  if (!section?.image_path) throw new Error('The customer photo was not saved');
  const imagePath = section.image_path;
  expect(readFileSync(path.join(projectFolder, imagePath))).toEqual(photoBytes);
  expect(requests.filter((request) => request.method === 'POST' && request.url.endsWith('/assets')))
    .toHaveLength(1);

  await page.getByRole('button', { name: 'Экспорт и деплой' }).click();
  page.once('dialog', (dialog) => void dialog.accept());
  await page.getByRole('button', { name: 'Экспортировать папку сайта' }).click();
  const exportPath = await page.getByRole('textbox', { name: 'Папка готового сайта' }).inputValue();
  expect(path.dirname(exportPath)).toBe(path.join(projectFolder, 'exports'));
  const html = readFileSync(path.join(exportPath, 'index.html'), 'utf8');
  expect(html).toContain('Текст клиента, отредактированный без API');
  expect(html).toContain('Услуги мастерской клиента');
  expect(html).toContain(imagePath);
  expect(readFileSync(path.join(exportPath, imagePath))).toEqual(photoBytes);

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Скачать ZIP сайта' }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('aurora-site.zip');
  const zipPath = await download.path();
  const inventory = JSON.parse(execFileSync(path.join(repository, '.venv', 'Scripts', 'python.exe'),
    ['-m', 'tests.browser.inspect_zip', zipPath], {
      cwd: repository, encoding: 'utf8', windowsHide: true,
    })) as { names: string[]; sha256: Record<string, string> };
  const members = ['index.html', 'assets/site.css', imagePath].sort();
  expect(inventory.names).toEqual(members);
  for (const name of members) {
    expect(inventory.sha256[name]).toBe(createHash('sha256')
      .update(readFileSync(path.join(exportPath, name))).digest('hex'));
  }

  await page.reload();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await page.getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('heading', { name: 'Сайт для экспорта' })).toBeVisible();
  expect(stored().editor.pages[0]?.sections[0]?.image_path).toBe(imagePath);
  await expect(page.getByRole('textbox', { name: 'Текст', exact: true })).toHaveValue('Текст клиента, отредактированный без API');
  await expect(page.getByText('Без API-доплат', { exact: true })).toBeVisible();
  expect(errors).toEqual([]);
  expect(requests.filter((request) => /^https?:/.test(request.url) && request.url !== origin &&
    !request.url.startsWith(`${origin}/`))).toEqual([]);
  expect(requests.filter((request) => /\/(generation|deployments|credentials)(\/|$)/
    .test(new URL(request.url).pathname))).toEqual([]);
});
