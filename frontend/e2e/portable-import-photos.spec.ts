import { randomUUID } from 'node:crypto';
import { expect, test } from '@playwright/test';

const origin = process.env.AURORA_PORTABLE_ORIGIN;
const projectName = 'Portable Customer Import';
const png = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/V9sAAAAASUVORK5CYII=',
  'base64',
);

interface ProjectMetadata { project_id: string; name: string }
interface ProjectDocument {
  metadata: ProjectMetadata;
  state: { editor: {
    brand: { logo_path: string | null };
    pages: { sections: { body: string; image_path: string | null; image_alt: string }[] }[];
  } };
}

test('packaged UI imports a local draft and attaches customer photos without a provider', async ({ page }) => {
  test.skip(!origin, 'Only the isolated portable Windows smoke supplies an origin');
  if (!origin || !/^http:\/\/127\.0\.0\.1:\d+$/.test(origin)) {
    throw new Error('Expected the packaged executable loopback origin');
  }
  const unexpectedRequests: string[] = [];
  const uploads: string[] = [];
  page.on('request', (request) => {
    const url = request.url();
    if (/^https?:/.test(url) && url !== origin && !url.startsWith(`${origin}/`)) {
      unexpectedRequests.push(url);
    }
    if (request.method() === 'POST' && /\/(generation|deployments)(\/|$)/.test(url)) {
      unexpectedRequests.push(url);
    }
    if (request.method() === 'POST' && url.endsWith('/assets')) uploads.push(url);
  });

  const listProjects = async (): Promise<ProjectMetadata[]> => {
    const response = await page.request.get(`${origin}/api/v1/projects`);
    expect(response.ok()).toBe(true);
    return await response.json() as ProjectMetadata[];
  };
  const existing = await listProjects();
  const pageId = randomUUID();
  const sectionId = randomUUID();
  const imported = {
    schema_version: 1, language: 'ru',
    brand: { name: 'Переносимая мастерская', tagline: 'Работаем вручную',
      primary_color: '#123456', secondary_color: '#abcdef', font_family: 'system', logo_path: null },
    pages: [{ id: pageId, slug: 'index', title: 'Мастерская',
      meta_description: 'Описание мастерской', heading: 'Добро пожаловать',
      sections: [{ id: sectionId, heading: 'Работы', body: 'Сайт из локального JSON',
        image_path: null, image_alt: 'Фото работ клиента' }] }],
  };
  const logoBytes = Buffer.concat([png, Buffer.from('portable-logo')]);
  const sectionBytes = Buffer.concat([png, Buffer.from('portable-section')]);

  await page.goto(origin);
  const firstLaunch = page.getByRole('button', { name: 'Русский' });
  const projectsHeading = page.getByRole('heading', { name: 'Проекты' });
  await expect(firstLaunch.or(projectsHeading).first()).toBeVisible();
  if (await firstLaunch.isVisible()) {
    await firstLaunch.click();
    await page.getByRole('button', { name: 'Начать' }).click();
  }
  await expect(projectsHeading).toBeVisible();
  await page.getByRole('textbox', { name: 'Название проекта' }).fill(projectName);
  await page.getByLabel('JSON-файл подготовленного сайта').setInputFiles({
    name: 'customer-site.json', mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(imported), 'utf8'),
  });
  await page.getByRole('button', { name: 'Импортировать подготовленный сайт' }).click();
  await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
  const projects = await listProjects();
  expect(projects).toHaveLength(existing.length + 1);
  for (const old of existing) expect(projects).toContainEqual(old);
  const project = projects.find((item) => item.name === projectName);
  if (!project) throw new Error('Imported project was not created');
  const openSaved = async (): Promise<ProjectDocument> => {
    const response = await page.request.get(`${origin}/api/v1/projects/${project.project_id}`);
    expect(response.ok()).toBe(true);
    return await response.json() as ProjectDocument;
  };
  expect((await openSaved()).state.editor.brand.logo_path).toBeNull();

  await page.getByRole('button', { name: 'Фотографии проекта' }).click();
  await page.getByLabel('Выбрать фотографии').setInputFiles([
    { name: 'portable-logo.png', mimeType: 'image/png', buffer: logoBytes },
    { name: 'portable-work.png', mimeType: 'image/png', buffer: sectionBytes },
  ]);
  const logoRow = page.locator('.photo-tray-item').filter({ hasText: 'portable-logo.png' });
  const sectionRow = page.locator('.photo-tray-item').filter({ hasText: 'portable-work.png' });
  await expect(logoRow).toBeVisible();
  await expect(sectionRow).toBeVisible();
  expect(uploads).toHaveLength(0);

  await logoRow.getByLabel('Куда прикрепить').selectOption('logo');
  await logoRow.getByRole('button', { name: 'Прикрепить фотографию' }).click();
  await expect(logoRow).toHaveCount(0);
  const logoPath = (await openSaved()).state.editor.brand.logo_path;
  expect(logoPath).toMatch(/^assets\/[a-f0-9]{64}\.png$/);
  if (!logoPath) throw new Error('Logo attachment was not saved');
  expect(uploads).toHaveLength(1);

  await sectionRow.getByLabel('Куда прикрепить').selectOption(`${pageId}/${sectionId}`);
  await sectionRow.getByRole('button', { name: 'Прикрепить фотографию' }).click();
  await expect(sectionRow).toHaveCount(0);
  const saved = await openSaved();
  const section = saved.state.editor.pages[0]?.sections[0];
  expect(section?.body).toBe('Сайт из локального JSON');
  expect(section?.image_alt).toBe('Фото работ клиента');
  expect(section?.image_path).toMatch(/^assets\/[a-f0-9]{64}\.png$/);
  if (!section?.image_path) throw new Error('Section attachment was not saved');
  expect(uploads).toHaveLength(2);

  for (const [assetPath, bytes] of [[logoPath, logoBytes], [section.image_path, sectionBytes]] as const) {
    const response = await page.request.get(`${origin}/api/v1/projects/${project.project_id}/${assetPath}`);
    expect(response.ok()).toBe(true);
    expect(Buffer.from(await response.body())).toEqual(bytes);
  }
  await page.getByRole('button', { name: 'Предпросмотр' }).click();
  await expect(page.frameLocator('iframe[title="Предпросмотр"]')
    .getByRole('img', { name: 'Фото работ клиента' })).toBeVisible();

  await page.reload();
  await expect(page.getByRole('heading', { name: 'Проекты' })).toBeVisible();
  await page.locator('.project-card').filter({ hasText: projectName })
    .getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
  await expect(page.getByRole('img', { name: 'Фото работ клиента' })).toBeVisible();
  expect((await openSaved()).state.editor.brand.logo_path).toBe(logoPath);
  expect((await openSaved()).state.editor.pages[0]?.sections[0]?.image_path).toBe(section.image_path);
  expect(unexpectedRequests).toEqual([]);
});
