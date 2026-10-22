import { execFileSync } from 'node:child_process';
import { createHash, randomUUID } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import path from 'node:path';
import { expect, test } from '@playwright/test';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = process.env.AURORA_PORTABLE_ORIGIN;
const projectsRoot = process.env.AURORA_PORTABLE_PROJECTS_ROOT;
const projectName = 'Portable Pasted Export';
const png = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/V9sAAAAASUVORK5CYII=',
  'base64',
);

interface ProjectMetadata { project_id: string; name: string }
interface ProjectDocument {
  metadata: ProjectMetadata;
  state: { editor: { brand: { name: string }; pages: {
    sections: { body: string; image_path: string | null; image_alt: string }[]
  }[] } };
}

test('packaged UI pastes a site, attaches a photo and exports matching folder and ZIP',
  async ({ page }) => {
    if (Boolean(origin) !== Boolean(projectsRoot)) {
      throw new Error('The packaged origin and isolated project root must be supplied together');
    }
    test.skip(!origin, 'Only the isolated portable Windows smoke supplies both paths');
    if (!origin || !/^http:\/\/127\.0\.0\.1:\d+$/.test(origin) || !projectsRoot) {
      throw new Error('Expected the packaged loopback origin and isolated project root');
    }
    const requests: { method: string; url: string }[] = [];
    page.on('request', (request) => requests.push({ method: request.method(), url: request.url() }));
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
      brand: { name: 'Мастерская для ZIP', tagline: 'Работаем вручную',
        primary_color: '#123456', secondary_color: '#abcdef', font_family: 'system', logo_path: null },
      pages: [{ id: pageId, slug: 'index', title: 'Мастерская для ZIP',
        meta_description: 'Услуги мастерской для ZIP', heading: 'Добро пожаловать',
        sections: [{ id: sectionId, heading: 'Работы', body: 'Сайт из portable JSON',
          image_path: null, image_alt: 'Фото работы клиента' }] }],
    };
    const photoBytes = Buffer.concat([png, Buffer.from('portable-paste-export')]);

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
    await page.getByRole('textbox', { name: 'Вставьте JSON подготовленного сайта' })
      .fill(JSON.stringify(imported));
    await page.getByRole('button', { name: 'Импортировать вставленный сайт' }).click();
    await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
    const projects = await listProjects();
    expect(projects).toHaveLength(existing.length + 1);
    for (const old of existing) expect(projects).toContainEqual(old);
    const project = projects.find((item) => item.name === projectName);
    if (!project) throw new Error('Portable pasted project was not created');
    const openSaved = async (): Promise<ProjectDocument> => {
      const response = await page.request.get(`${origin}/api/v1/projects/${project.project_id}`);
      expect(response.ok()).toBe(true);
      return await response.json() as ProjectDocument;
    };
    expect((await openSaved()).state.editor.pages[0]?.sections[0]?.image_path).toBeNull();

    await page.getByRole('button', { name: 'Фотографии проекта' }).click();
    await page.getByLabel('Выбрать фотографии').setInputFiles({
      name: 'portable-client.png', mimeType: 'image/png', buffer: photoBytes,
    });
    const photoRow = page.locator('.photo-tray-item').filter({ hasText: 'portable-client.png' });
    await expect(photoRow).toBeVisible();
    expect(requests.filter((request) => request.method === 'POST' && request.url.endsWith('/assets')))
      .toHaveLength(0);
    await photoRow.getByLabel('Куда прикрепить').selectOption(`${pageId}/${sectionId}`);
    await photoRow.getByRole('button', { name: 'Прикрепить фотографию' }).click();
    await expect(photoRow).toHaveCount(0);
    const section = (await openSaved()).state.editor.pages[0]?.sections[0];
    expect(section?.body).toBe('Сайт из portable JSON');
    expect(section?.image_alt).toBe('Фото работы клиента');
    expect(section?.image_path).toMatch(/^assets\/[a-f0-9]{64}\.png$/);
    if (!section?.image_path) throw new Error('Portable customer photo was not saved');
    const imagePath = section.image_path;
    const asset = await page.request.get(`${origin}/api/v1/projects/${project.project_id}/${imagePath}`);
    expect(asset.ok()).toBe(true);
    expect(Buffer.from(await asset.body())).toEqual(photoBytes);
    expect(requests.filter((request) => request.method === 'POST' && request.url.endsWith('/assets')))
      .toHaveLength(1);

    await page.getByRole('button', { name: 'Экспорт и деплой' }).click();
    page.once('dialog', (dialog) => void dialog.accept());
    await page.getByRole('button', { name: 'Экспортировать папку сайта' }).click();
    const exportPath = realpathSync(path.resolve(await page
      .getByRole('textbox', { name: 'Папка готового сайта' }).inputValue()));
    const projectFolder = path.dirname(path.dirname(exportPath));
    expect(path.dirname(projectFolder)).toBe(realpathSync(projectsRoot));
    expect(path.dirname(exportPath)).toBe(path.join(projectFolder, 'exports'));
    const metadata = JSON.parse(readFileSync(path.join(projectFolder, 'aurora.project.json'), 'utf8')) as
      { project_id: string };
    expect(metadata.project_id).toBe(project.project_id);
    const html = readFileSync(path.join(exportPath, 'index.html'), 'utf8');
    expect(html).toContain('Сайт из portable JSON');
    expect(html).toContain('Услуги мастерской для ZIP');
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
    await expect(projectsHeading).toBeVisible();
    await page.locator('.project-card').filter({ hasText: projectName })
      .getByRole('button', { name: 'Открыть' }).click();
    await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
    expect((await openSaved()).state.editor.pages[0]?.sections[0]?.image_path).toBe(imagePath);
    expect(requests.filter((request) => /^https?:/.test(request.url) && request.url !== origin &&
      !request.url.startsWith(`${origin}/`))).toEqual([]);
    expect(requests.filter((request) => /\/(generation|deployments)(\/|$)/
      .test(new URL(request.url).pathname))).toEqual([]);
  });
