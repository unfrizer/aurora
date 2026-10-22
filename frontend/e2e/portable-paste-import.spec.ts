import { randomUUID } from 'node:crypto';
import { expect, test } from '@playwright/test';

const origin = process.env.AURORA_PORTABLE_ORIGIN;
const projectName = 'Portable Pasted Import';

interface ProjectMetadata { project_id: string; name: string }
interface ProjectDocument { metadata: ProjectMetadata; state: { editor: unknown } }

test('packaged UI pastes, previews and reopens a prepared site without a provider', async ({ page }) => {
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
    const pathname = new URL(url).pathname;
    if (/\/(generation|deployments)(\/|$)/.test(pathname) ||
        ((request.method() === 'POST' || request.method() === 'DELETE') &&
          /\/assets(\/|$)/.test(pathname))) unexpectedRequests.push(url);
  });

  const listProjects = async (): Promise<ProjectMetadata[]> => {
    const response = await page.request.get(`${origin}/api/v1/projects`);
    expect(response.ok()).toBe(true);
    return await response.json() as ProjectMetadata[];
  };
  const existing = await listProjects();
  const imported = {
    schema_version: 1, language: 'ru',
    brand: { name: 'Портативная студия', tagline: 'Готово к работе',
      primary_color: '#123456', secondary_color: '#abcdef', font_family: 'system', logo_path: null },
    pages: [{ id: randomUUID(), slug: 'index', title: 'Портативная студия',
      meta_description: 'Описание студии', heading: 'Добро пожаловать',
      sections: [{ id: randomUUID(), heading: 'О нас', body: 'Сайт из вставленного JSON',
        image_path: null, image_alt: '' }] }],
  };

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
  const paste = page.getByRole('textbox', { name: 'Вставьте JSON подготовленного сайта' });
  await paste.fill('{');
  await page.getByRole('button', { name: 'Импортировать вставленный сайт' }).click();
  await expect(page.getByText('Файл импорта не содержит корректный JSON.')).toBeVisible();
  expect(await listProjects()).toEqual(existing);

  await page.getByLabel('JSON-файл подготовленного сайта').setInputFiles({
    name: 'invalid.json', mimeType: 'application/json', buffer: Buffer.from('{'),
  });
  await paste.fill(JSON.stringify(imported));
  await page.getByRole('button', { name: 'Импортировать вставленный сайт' }).click();
  await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
  const projects = await listProjects();
  expect(projects).toHaveLength(existing.length + 1);
  for (const old of existing) expect(projects).toContainEqual(old);
  const project = projects.find((item) => item.name === projectName);
  if (!project) throw new Error('Pasted project was not created');
  const openSaved = async (): Promise<ProjectDocument> => {
    const response = await page.request.get(`${origin}/api/v1/projects/${project.project_id}`);
    expect(response.ok()).toBe(true);
    return await response.json() as ProjectDocument;
  };
  const saved = await openSaved();
  expect(saved.metadata.project_id).toBe(project.project_id);
  expect(saved.state.editor).toEqual(imported);

  await page.getByRole('button', { name: 'Предпросмотр' }).click();
  const preview = page.frameLocator('iframe[title="Предпросмотр"]');
  await expect(preview.getByRole('heading', { name: 'Добро пожаловать' })).toBeVisible();
  await expect(preview.getByText('Сайт из вставленного JSON')).toBeVisible();

  await page.reload();
  await expect(projectsHeading).toBeVisible();
  await page.locator('.project-card').filter({ hasText: projectName })
    .getByRole('button', { name: 'Открыть' }).click();
  await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
  expect((await openSaved()).state.editor).toEqual(imported);
  expect(unexpectedRequests).toEqual([]);
});
