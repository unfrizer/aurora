import { spawn, type ChildProcess } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { once } from 'node:events';
import { mkdirSync, readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { expect, test } from '@playwright/test';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = 'http://127.0.0.1:18765';
let server: ChildProcess | null = null;
let dataRoot = '';

test.beforeAll(async () => {
  let occupied = false;
  try { await fetch(`${origin}/api/v1/health`); occupied = true; }
  catch { /* The test port is not serving HTTP. */ }
  if (occupied) throw new Error('The browser test port is already in use');
  const build = path.join(repository, 'build');
  mkdirSync(build, { recursive: true });
  dataRoot = path.join(build, `browser-e2e-${randomUUID()}`);
  server = spawn(path.join(repository, '.venv', 'Scripts', 'python.exe'),
    ['-m', 'tests.browser.server'], {
      cwd: repository,
      env: { ...process.env, AURORA_E2E_ROOT: dataRoot, AURORA_E2E_PORT: '18765' },
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

function projectFolder(projectsDirectory: string): string {
  const names = readdirSync(projectsDirectory, { withFileTypes: true })
    .filter((entry) => entry.isDirectory()).map((entry) => entry.name);
  expect(names).toHaveLength(1);
  return path.join(projectsDirectory, names[0]!);
}

interface PersistedEditor {
  editor: {
    brand: { name: string; logo_path: string | null };
    pages: { meta_description: string; sections: { image_path: string | null; image_alt: string }[] }[];
  };
}

test('one-prompt, image and editor browser journey uses only isolated fake services', async ({ page }) => {
  const imageRequests: string[] = [];
  page.on('request', (request) => {
    if (request.method() === 'POST' && request.url().endsWith('/generation/image')) {
      imageRequests.push(request.postData() ?? '');
    }
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Русский' }).click();
  await page.getByRole('button', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();

  await page.getByRole('button', { name: 'Настройки' }).click();
  const openAI = page.locator('.setting-secret').filter({ hasText: 'Ключ OpenAI' });
  await openAI.getByLabel('Ключ OpenAI').fill('qa-only-fake-key');
  await openAI.getByRole('button', { name: 'Сохранить ключ' }).click();
  await expect(openAI.getByText('Подключено')).toBeVisible();
  const projectsDirectory = await page.locator('label')
    .filter({ hasText: 'Папка проектов (только просмотр)' }).locator('output').innerText();
  expect(projectsDirectory).toBe(path.join(dataRoot, 'Projects'));

  await page.getByRole('button', { name: 'Проекты' }).click();
  await page.getByRole('textbox', { name: 'Название проекта' }).fill('QA Browser Studio');
  await page.getByRole('textbox', { name: 'Опишите бизнес одним запросом' })
    .fill('Создай сайт небольшой дизайн-студии.');
  page.once('dialog', (dialog) => void dialog.accept());
  await page.getByRole('button', { name: 'Создать из запроса' }).click();
  await expect(page.getByRole('heading', { name: 'Просмотр черновика' })).toBeVisible();
  await expect(page.getByText('Северная студия', { exact: true })).toBeVisible();
  expect(readFileSync(path.join(projectFolder(projectsDirectory), 'state.json'), 'utf8'))
    .not.toContain('"editor"');

  await page.getByRole('button', { name: 'Принять и сохранить' }).click();
  await expect(page.getByRole('heading', { name: 'Добавить изображения к проекту' })).toBeVisible();
  const folder = projectFolder(projectsDirectory);
  const storedEditor = (): PersistedEditor =>
    JSON.parse(readFileSync(path.join(folder, 'state.json'), 'utf8')) as PersistedEditor;
  await expect(page.getByText(/Возможных первых платных запросов: 2/)).toBeVisible();
  await page.getByRole('button', { name: 'Посмотреть план изображений' }).click();
  await expect(page.getByText('Create a brand logo for "Северная студия". Tagline: "Дизайн для бизнеса". Language: ru.')).toBeVisible();
  await page.getByRole('button', { name: 'Просмотреть и создать изображение' }).click();
  const imageDialog = page.getByRole('dialog', { name: 'Сгенерировать изображение' });
  await expect(imageDialog.getByRole('textbox', { name: 'Опишите нужное изображение' }))
    .toHaveValue('Create a brand logo for "Северная студия". Tagline: "Дизайн для бизнеса". Language: ru.');
  page.once('dialog', (dialog) => void dialog.dismiss());
  await imageDialog.getByRole('button', { name: 'Сгенерировать изображение' }).click();
  expect(imageRequests).toHaveLength(0);
  expect(storedEditor().editor.brand.logo_path).toBeNull();

  page.once('dialog', (dialog) => void dialog.accept());
  await imageDialog.getByRole('button', { name: 'Сгенерировать изображение' }).click();
  await expect(imageDialog.getByText('Сохранено в проекте, но не прикреплено')).toBeVisible();
  expect(imageRequests).toHaveLength(1);
  await expect.poll(() => imageDialog.locator('img.image-candidate')
    .evaluate((image) => (image as HTMLImageElement).naturalWidth)).toBe(1);
  expect(storedEditor().editor.brand.logo_path).toBeNull();
  expect(readdirSync(path.join(folder, 'assets'))).toHaveLength(1);
  await imageDialog.getByRole('button', { name: 'Прикрепить и сохранить' }).click();
  await expect(imageDialog).toHaveCount(0);
  const logoPath = storedEditor().editor.brand.logo_path;
  expect(logoPath).toMatch(/^assets\/[a-f0-9]{64}\.png$/);

  await expect(page.getByRole('heading', { name: 'Северная студия / Услуги' })).toBeVisible();
  await page.getByRole('button', { name: 'Просмотреть и создать изображение' }).click();
  const sectionGenerate = imageDialog.getByRole('button', { name: 'Сгенерировать изображение' });
  await expect(imageDialog.getByRole('textbox', { name: 'Опишите нужное изображение' }))
    .toHaveValue('Create an image for page "Добро пожаловать", section "Услуги", brand "Северная студия". Language: ru.');
  await expect(sectionGenerate).toBeDisabled();
  await imageDialog.getByRole('textbox', { name: 'Введите описание изображения для секции.' })
    .fill('Изображение тестовой секции');
  await expect(sectionGenerate).toBeEnabled();
  page.once('dialog', (dialog) => void dialog.accept());
  await sectionGenerate.click();
  await expect(imageDialog.getByText('Сохранено в проекте, но не прикреплено')).toBeVisible();
  expect(imageRequests).toHaveLength(2);
  expect(storedEditor().editor.pages[0]?.sections[0]?.image_path).toBeNull();
  await imageDialog.getByRole('button', { name: 'Прикрепить и сохранить' }).click();
  await expect(imageDialog).toHaveCount(0);
  const section = storedEditor().editor.pages[0]?.sections[0];
  const sectionPath = section?.image_path;
  expect(sectionPath).toMatch(/^assets\/[a-f0-9]{64}\.png$/);
  if (!sectionPath) throw new Error('The section image was not saved');
  expect(section?.image_alt).toBe('Изображение тестовой секции');
  await expect(page.getByText('Все места в этом плане заполнены. Проект сохранён и готов к дальнейшему редактированию.')).toBeVisible();
  expect(imageRequests).toHaveLength(2);

  await page.getByRole('button', { name: 'Перейти в редактор' }).click();
  await expect(page.getByRole('heading', { name: 'QA Browser Studio' })).toBeVisible();
  const brandName = page.locator('.side.right').getByRole('textbox', { name: 'Название бренда' });
  await brandName.fill('Северная студия — обновлено');
  await brandName.press('Tab');
  await expect.poll(() => storedEditor().editor.brand.name).toBe('Северная студия — обновлено');

  const seoDescription = page.locator('.page-title').getByRole('textbox', { name: 'Meta description' });
  await seoDescription.fill('Обновлённое описание для браузерного теста.');
  await seoDescription.press('Tab');
  await expect.poll(() => storedEditor().editor.pages[0]?.meta_description)
    .toBe('Обновлённое описание для браузерного теста.');

  const workspace = page.locator('.workspace');
  await page.getByRole('button', { name: 'Toggle Страницы' }).click();
  await expect(workspace).toHaveClass(/left-collapsed/);
  await expect(workspace).not.toHaveClass(/right-collapsed/);
  await page.getByRole('button', { name: 'Toggle Инспектор / AI' }).click();
  await expect(workspace).toHaveClass(/left-collapsed/);
  await expect(workspace).toHaveClass(/right-collapsed/);
  await page.getByRole('button', { name: 'Toggle Страницы' }).click();
  await expect(workspace).not.toHaveClass(/left-collapsed/);
  await expect(workspace).toHaveClass(/right-collapsed/);
  await page.getByRole('button', { name: 'Toggle Инспектор / AI' }).click();
  await expect(workspace).not.toHaveClass(/right-collapsed/);

  const body = page.getByRole('textbox', { name: 'Текст' });
  await body.fill('Изменённый текст браузерного теста.');
  await body.press('Tab');
  await page.getByRole('button', { name: 'Сохранить', exact: true }).click();
  await expect.poll(() => readFileSync(path.join(projectFolder(projectsDirectory), 'state.json'), 'utf8'))
    .toContain('Изменённый текст браузерного теста.');

  await page.getByRole('button', { name: 'Предпросмотр' }).click();
  const preview = page.frameLocator('iframe[title="Предпросмотр"]');
  await expect(preview.getByText('Изменённый текст браузерного теста.')).toBeVisible();
  await expect(preview.locator('meta[name="description"]'))
    .toHaveAttribute('content', 'Обновлённое описание для браузерного теста.');
  await expect(preview.getByRole('img', { name: 'Изображение тестовой секции' })).toBeVisible();
  await expect.poll(() => preview.getByRole('img', { name: 'Изображение тестовой секции' })
    .evaluate((image) => (image as HTMLImageElement).naturalWidth)).toBe(1);
  await page.getByRole('button', { name: 'Телефон' }).click();
  await expect(page.locator('.preview-frame.mobile')).toBeVisible();
  await page.getByRole('button', { name: 'Компьютер' }).click();
  await expect(page.locator('.preview-frame')).not.toHaveClass(/mobile/);
  const previewTabPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Открыть в браузере' }).click();
  const previewTab = await previewTabPromise;
  await expect(previewTab).toHaveURL(new RegExp(`^${origin.replaceAll('.', '\\.')}/api/v1/projects/`));
  await expect(previewTab.getByText('Изменённый текст браузерного теста.')).toBeVisible();
  await previewTab.close();
  await page.getByRole('button', { name: 'Экспорт и деплой' }).click();
  page.once('dialog', (dialog) => void dialog.accept());
  await page.getByRole('button', { name: 'Экспортировать папку сайта' }).click();
  const exportPath = await page.getByRole('textbox', { name: 'Папка готового сайта' }).inputValue();
  expect(path.dirname(exportPath)).toBe(path.join(projectFolder(projectsDirectory), 'exports'));
  expect(readFileSync(path.join(exportPath, 'index.html'), 'utf8'))
    .toContain('Изменённый текст браузерного теста.');
  expect(readFileSync(path.join(exportPath, 'index.html'), 'utf8'))
    .toContain('Обновлённое описание для браузерного теста.');
  expect(readFileSync(path.join(exportPath, 'index.html'), 'utf8')).toContain(sectionPath);
  expect(readFileSync(path.join(exportPath, sectionPath)))
    .toEqual(readFileSync(path.join(folder, sectionPath)));
  expect(readdirSync(exportPath)).toEqual(['assets', 'index.html']);

  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Скачать ZIP сайта' }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('aurora-site.zip');
  expect(statSync(await download.path()).size).toBeGreaterThan(0);

  await page.reload();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Добро пожаловать в AURORA' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('textbox', { name: 'Текст' }))
    .toHaveValue('Изменённый текст браузерного теста.');
  await expect(page.locator('.side.right').getByRole('textbox', { name: 'Название бренда' }))
    .toHaveValue('Северная студия — обновлено');
  await expect(page.locator('.page-title').getByRole('textbox', { name: 'Meta description' }))
    .toHaveValue('Обновлённое описание для браузерного теста.');
  await expect(page.getByRole('img', { name: 'Изображение тестовой секции' })).toBeVisible();
  expect(storedEditor().editor.brand.logo_path).toBe(logoPath);
  expect(storedEditor().editor.pages[0]?.sections[0]?.image_path).toBe(sectionPath);

  for (const file of [path.join(dataRoot, 'settings.json'),
    path.join(projectFolder(projectsDirectory), 'aurora.project.json'),
    path.join(projectFolder(projectsDirectory), 'state.json')]) {
    expect(readFileSync(file, 'utf8')).not.toContain('qa-only-fake-key');
  }
});
