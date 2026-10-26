import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import path from 'node:path';
import { expect, test } from '@playwright/test';

const repository = path.resolve(import.meta.dirname, '../..');
const origin = process.env.AURORA_PORTABLE_ORIGIN;
const projectsRoot = process.env.AURORA_PORTABLE_PROJECTS_ROOT;
const projectName = 'Portable Brief Starter';
const brief = '  Настройка велосипедов\nРемонт и диагностика  ';

interface ProjectMetadata { project_id: string; name: string; updated_at: string }
interface ProjectDocument {
  metadata: ProjectMetadata;
  state: { editor: {
    schema_version: number;
    language: string;
    brand: { name: string; tagline: string; logo_path: string | null };
    pages: { slug: string; meta_description: string;
      sections: { body: string; image_path: string | null }[] }[];
  } };
}

test('packaged UI creates, exports and reopens an offline brief after explicit consent',
  async ({ page }) => {
    if (Boolean(origin) !== Boolean(projectsRoot)) {
      throw new Error('The packaged origin and isolated project root must be supplied together');
    }
    test.skip(!origin, 'Only the isolated portable Windows smoke supplies both paths');
    if (!origin || !/^http:\/\/127\.0\.0\.1:\d+$/.test(origin) || !projectsRoot) {
      throw new Error('Expected the packaged loopback origin and isolated project root');
    }
    const requests: { method: string; url: string; body: string | null }[] = [];
    page.on('request', (request) => requests.push({
      method: request.method(), url: request.url(), body: request.postData(),
    }));
    const listProjects = async (): Promise<ProjectMetadata[]> => {
      const response = await page.request.get(`${origin}/api/v1/projects`);
      expect(response.ok()).toBe(true);
      return await response.json() as ProjectMetadata[];
    };
    const existing = await listProjects();

    await page.goto(origin);
    const firstLaunch = page.getByRole('button', { name: 'Русский' });
    const projectsHeading = page.getByRole('heading', { name: 'Проекты' });
    await expect(firstLaunch.or(projectsHeading).first()).toBeVisible();
    if (await firstLaunch.isVisible()) {
      await firstLaunch.click();
      await page.getByRole('button', { name: 'Начать' }).click();
    }
    await expect(projectsHeading).toBeVisible();
    const name = page.getByRole('textbox', { name: 'Название проекта' });
    await name.fill(projectName);
    await page.getByRole('textbox', { name: 'ТЗ для офлайн-старта' }).fill(brief);
    await expect(page.getByText(/Это не приватная заметка/)).toBeVisible();
    await name.press('Enter');
    await expect(projectsHeading).toBeVisible();
    let publicWarning = '';
    page.once('dialog', (dialog) => { publicWarning = dialog.message(); void dialog.dismiss(); });
    await page.getByRole('button', { name: 'Создать проект с ТЗ' }).click();
    expect(publicWarning).toContain('ТЗ будет без изменений видно на сайте');
    expect(await listProjects()).toEqual(existing);
    expect(requests.filter((request) => request.method === 'POST' &&
      request.url === `${origin}/api/v1/projects`)).toHaveLength(0);
    expect(requests.filter((request) => request.method === 'PUT' &&
      /\/projects\/[^/]+\/editor$/.test(new URL(request.url).pathname))).toHaveLength(0);

    const createdResponse = page.waitForResponse((response) =>
      response.url() === `${origin}/api/v1/projects` && response.request().method() === 'POST');
    page.once('dialog', (dialog) => void dialog.accept());
    await page.getByRole('button', { name: 'Создать проект с ТЗ' }).click();
    const created = await (await createdResponse).json() as ProjectDocument;
    await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
    const projects = await listProjects();
    expect(projects).toHaveLength(existing.length + 1);
    for (const old of existing) expect(projects).toContainEqual(old);
    const project = projects.find((item) => item.project_id === created.metadata.project_id);
    expect(project?.name).toBe(projectName);
    const openSaved = async (): Promise<ProjectDocument> => {
      const response = await page.request.get(`${origin}/api/v1/projects/${created.metadata.project_id}`);
      expect(response.ok()).toBe(true);
      return await response.json() as ProjectDocument;
    };
    const saved = await openSaved();
    expect(saved.metadata.project_id).toBe(created.metadata.project_id);
    expect(saved.state.editor).toMatchObject({
      schema_version: 1, language: 'ru',
      brand: { name: projectName, tagline: '', logo_path: null },
      pages: [{ slug: 'index', meta_description: '',
        sections: [{ body: brief, image_path: null }] }],
    });
    expect(saved.state.editor.pages).toHaveLength(1);
    expect(saved.state.editor.pages[0]?.sections).toHaveLength(1);
    const creates = requests.filter((request) => request.method === 'POST' &&
      request.url === `${origin}/api/v1/projects`);
    const saves = requests.filter((request) => request.method === 'PUT' &&
      /^\/api\/v1\/projects\/[^/]+\/editor$/.test(new URL(request.url).pathname));
    expect(creates).toHaveLength(1);
    expect(saves).toHaveLength(1);
    expect(new URL(saves[0]!.url).pathname)
      .toBe(`/api/v1/projects/${created.metadata.project_id}/editor`);
    expect(JSON.parse(saves[0]?.body ?? '{}') as { expected_updated_at?: unknown })
      .toMatchObject({ expected_updated_at: created.metadata.updated_at });

    await page.getByRole('button', { name: 'Предпросмотр' }).click();
    const preview = page.frameLocator('iframe[title="Предпросмотр"]');
    await expect(preview.getByText(/Настройка велосипедов/)).toBeVisible();
    await expect(preview.getByText(/Ремонт и диагностика/)).toBeVisible();
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
    expect(metadata.project_id).toBe(created.metadata.project_id);
    const html = readFileSync(path.join(exportPath, 'index.html'), 'utf8');
    expect(html).toContain('Настройка велосипедов');
    expect(html).toContain('Ремонт и диагностика');

    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Скачать ZIP сайта' }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe('aurora-site.zip');
    const inventory = JSON.parse(execFileSync(path.join(repository, '.venv', 'Scripts', 'python.exe'),
      ['-m', 'tests.browser.inspect_zip', await download.path()], {
        cwd: repository, encoding: 'utf8', windowsHide: true,
      })) as { names: string[]; sha256: Record<string, string> };
    const members = ['index.html', 'assets/site.css'].sort();
    expect(inventory.names).toEqual(members);
    for (const member of members) {
      expect(inventory.sha256[member]).toBe(createHash('sha256')
        .update(readFileSync(path.join(exportPath, member))).digest('hex'));
    }

    await page.reload();
    await expect(projectsHeading).toBeVisible();
    await page.locator('.project-card').filter({ hasText: projectName })
      .getByRole('button', { name: 'Открыть' }).click();
    await expect(page.getByRole('heading', { name: projectName })).toBeVisible();
    await expect(page.getByRole('textbox', { name: 'Текст' })).toHaveValue(brief);
    expect((await openSaved()).state.editor.pages[0]?.sections[0]?.body).toBe(brief);
    expect(requests.filter((request) => /^https?:/.test(request.url) && request.url !== origin &&
      !request.url.startsWith(`${origin}/`))).toEqual([]);
    expect(requests.filter((request) => {
      const pathname = new URL(request.url).pathname;
      return /\/(generation|deployments|credentials)(\/|$)/.test(pathname) ||
        ((request.method === 'POST' || request.method === 'DELETE') && /\/assets(\/|$)/.test(pathname));
    })).toEqual([]);
  });
