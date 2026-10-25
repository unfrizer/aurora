import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { EditorDocument, ProjectDocument } from '../src/types';
import { blankEditor } from '../src/editor';

const originalPhotoUrl = Object.getOwnPropertyDescriptor(URL, 'createObjectURL');
const originalPhotoRevoke = Object.getOwnPropertyDescriptor(URL, 'revokeObjectURL');

function stubPhotoUrls() {
  Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: vi.fn(() => 'blob:customer-photo') });
  Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() });
}

function importFile(editor: EditorDocument): File {
  const bytes = new TextEncoder().encode(JSON.stringify(editor));
  const selected = new File([Uint8Array.from(bytes).buffer], 'prepared.json', { type: 'application/json' });
  Object.defineProperty(selected, 'arrayBuffer', { value: async () => Uint8Array.from(bytes).buffer });
  return selected;
}

const mocks = vi.hoisted(() => ({
  getPreferences: vi.fn(), savePreferences: vi.fn(),
  listProjects: vi.fn(), createProject: vi.fn(), openProject: vi.fn(), saveEditor: vi.fn(),
  renameProject: vi.fn(), deleteProject: vi.fn(), credentialStatus: vi.fn(),
  setCredential: vi.fn(), deleteCredential: vi.fn(), exportFolder: vi.fn(), exportZip: vi.fn(), deployNetlify: vi.fn(),
  generateText: vi.fn(), uploadRaster: vi.fn(), deleteRaster: vi.fn(),
  generateProjectDraft: vi.fn(),
  generateImage: vi.fn(),
}));

vi.mock('../src/api', async (original) => ({ ...(await original<typeof import('../src/api')>()), ...mocks }));

import App from '../src/App';
import { ApiError } from '../src/api';
import { ExportDeploy } from '../src/components/ExportDeploy';
import { preparedSitePrompt, preparedSitePromptWithBrief } from '../src/prepared_site_prompt';

const id = '00000000-0000-4000-8000-000000000111';
const metadata = { project_id: id, name: 'Studio', format_version: '1', created_at: '2026-10-09T00:00:00Z', updated_at: '2026-10-09T01:00:00Z' };
const empty: ProjectDocument = { metadata, state: {} };

function withEditor(editor: EditorDocument): ProjectDocument {
  return { metadata: { ...metadata, updated_at: '2026-10-09T02:00:00Z' }, state: { editor } };
}

async function enter(language: 'ru' | 'en' = 'en') {
  render(<App />);
  fireEvent.click(await screen.findByRole('button', { name: language === 'en' ? 'English' : 'Русский' }));
  fireEvent.click(await screen.findByRole('button', { name: language === 'en' ? 'Start' : 'Начать' }));
  await screen.findByRole('heading', { name: language === 'en' ? 'Projects' : 'Проекты' });
}

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getPreferences.mockResolvedValue({
    preferences: { schema_version: 1, language: null, onboarding_completed: false,
      general_model: 'gpt-5.6-terra', image_model: 'gpt-image-2' },
    revision: 'a'.repeat(64), projects_directory: 'C:\\Projects',
  });
  mocks.savePreferences.mockImplementation(async (preferences: object) => ({ preferences, revision: 'b'.repeat(64) }));
  mocks.listProjects.mockResolvedValue([metadata]);
  mocks.createProject.mockResolvedValue(empty);
  mocks.openProject.mockResolvedValue(withEditor(blankEditor('Studio', 'en')));
  mocks.saveEditor.mockImplementation(async (_projectId: string, editor: EditorDocument) => withEditor(editor));
  mocks.credentialStatus.mockResolvedValue(false);
  mocks.setCredential.mockResolvedValue(undefined);
  mocks.deleteCredential.mockResolvedValue(undefined);
  mocks.renameProject.mockImplementation(async (doc: ProjectDocument, name: string) => ({ ...doc, metadata: { ...doc.metadata, name } }));
  mocks.deleteProject.mockResolvedValue(undefined);
  mocks.generateProjectDraft.mockResolvedValue({ job_id: id, status: 'completed',
    source_updated_at: metadata.updated_at, editor: blankEditor('Studio', 'en'), failure: null });
  mocks.generateImage.mockResolvedValue({ job_id: id, status: 'completed',
    source_updated_at: '2026-10-09T02:00:00Z', asset_path: `assets/${'a'.repeat(64)}.png`, failure: null });
});

afterEach(() => {
  vi.unstubAllGlobals();
  if (originalPhotoUrl) Object.defineProperty(URL, 'createObjectURL', originalPhotoUrl);
  else Reflect.deleteProperty(URL, 'createObjectURL');
  if (originalPhotoRevoke) Object.defineProperty(URL, 'revokeObjectURL', originalPhotoRevoke);
  else Reflect.deleteProperty(URL, 'revokeObjectURL');
});

describe('UI-008 customer photos', () => {
  async function openTray(file: File) {
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    fireEvent.click(screen.getByRole('button', { name: 'Project photos' }));
    fireEvent.change(screen.getByLabelText('Choose photos'), { target: { files: [file] } });
  }

  it('uploads only after manual destination selection, then saves without provider calls', async () => {
    stubPhotoUrls();
    const existing = blankEditor('Studio', 'en');
    existing.pages[0]!.sections[0]!.image_alt = 'Customer-supplied image';
    mocks.openProject.mockResolvedValue(withEditor(existing));
    const path = `assets/${'a'.repeat(64)}.png`;
    const steps: string[] = [];
    mocks.uploadRaster.mockImplementation(async () => { steps.push('upload'); return path; });
    mocks.saveEditor.mockImplementation(async (_projectId: string, next: EditorDocument) => {
      steps.push('save'); return withEditor(next);
    });
    const file = new File(['png'], 'customer.png', { type: 'image/png' });
    await openTray(file);
    expect(mocks.uploadRaster).not.toHaveBeenCalled();
    const page = existing.pages[0]!;
    const section = page.sections[0]!;
    fireEvent.change(screen.getByLabelText('Attach to'), { target: { value: `${page.id}/${section.id}` } });
    fireEvent.click(screen.getByRole('button', { name: 'Attach photo' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    expect(steps).toEqual(['upload', 'save']);
    expect(mocks.uploadRaster).toHaveBeenCalledExactlyOnceWith(id, file);
    expect(mocks.saveEditor.mock.calls[0]?.[2]).toBe('2026-10-09T02:00:00Z');
    expect((mocks.saveEditor.mock.calls[0]?.[1] as EditorDocument).pages[0]?.sections[0])
      .toMatchObject({ image_path: path, image_alt: 'Customer-supplied image' });
    await waitFor(() => expect(screen.queryByText('customer.png')).not.toBeInTheDocument());
    expect(mocks.generateImage).not.toHaveBeenCalled();
    expect(mocks.generateText).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(mocks.deployNetlify).not.toHaveBeenCalled();
  });

  it('keeps the selected photo after a failed save and does not retry or delete it', async () => {
    stubPhotoUrls();
    const path = `assets/${'b'.repeat(64)}.png`;
    mocks.uploadRaster.mockResolvedValue(path);
    mocks.saveEditor.mockRejectedValue(new ApiError(409));
    await openTray(new File(['png'], 'waiting.png', { type: 'image/png' }));
    fireEvent.change(screen.getByLabelText('Attach to'), { target: { value: 'logo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Attach photo' }));
    expect(await screen.findByText(/Attachment is not confirmed/)).toBeInTheDocument();
    expect(screen.getByText('waiting.png')).toBeInTheDocument();
    expect(mocks.uploadRaster).toHaveBeenCalledTimes(1);
    expect(mocks.saveEditor).toHaveBeenCalledTimes(1);
    expect(mocks.deleteRaster).not.toHaveBeenCalled();
    await waitFor(() => expect(screen.getByRole('button', { name: 'Projects' })).toBeEnabled());
  });

  it('deletes a replaced old asset only after a confirmed save and no remaining reference', async () => {
    stubPhotoUrls();
    const old = `assets/${'c'.repeat(64)}.png`;
    const next = `assets/${'d'.repeat(64)}.png`;
    const existing = blankEditor('Studio', 'en');
    existing.brand.logo_path = old;
    mocks.openProject.mockResolvedValue(withEditor(existing));
    mocks.uploadRaster.mockResolvedValue(next);
    const steps: string[] = [];
    mocks.saveEditor.mockImplementation(async (_projectId: string, editor: EditorDocument) => {
      steps.push('save'); return withEditor(editor);
    });
    mocks.deleteRaster.mockImplementation(async () => { steps.push('delete'); });
    await openTray(new File(['png'], 'new-logo.png', { type: 'image/png' }));
    fireEvent.change(screen.getByLabelText('Attach to'), { target: { value: 'logo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Attach photo' }));
    await waitFor(() => expect(mocks.deleteRaster).toHaveBeenCalledWith(id, `${'c'.repeat(64)}.png`));
    expect((mocks.saveEditor.mock.calls[0]?.[1] as EditorDocument).brand.logo_path).toBe(next);
    expect(mocks.saveEditor).toHaveBeenCalledTimes(1);
    expect(steps).toEqual(['save', 'delete']);
  });
});

describe('UI-007 prepared site import', () => {
  const importedId = '00000000-0000-4000-8000-000000000777';
  const importedMetadata = { ...metadata, project_id: importedId, name: 'Imported', updated_at: '2026-10-20T01:00:00Z' };

  async function select(editor: EditorDocument, language: 'ru' | 'en' = 'en') {
    await enter(language);
    fireEvent.change(screen.getByLabelText(language === 'en' ? 'Project name' : 'Название проекта'),
      { target: { value: 'Imported' } });
    fireEvent.change(screen.getByLabelText(language === 'en' ? 'Prepared site JSON file' : 'JSON-файл подготовленного сайта'),
      { target: { files: [importFile(editor)] } });
    fireEvent.click(screen.getByRole('button', {
      name: language === 'en' ? 'Import prepared site' : 'Импортировать подготовленный сайт',
    }));
  }

  it('creates a separate new project and versioned P7 save without provider or deployment calls', async () => {
    const prepared = blankEditor('Imported', 'en');
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    mocks.saveEditor.mockImplementation(async (_id: string, editor: EditorDocument) =>
      ({ metadata: { ...importedMetadata, updated_at: '2026-10-20T02:00:00Z' }, state: { editor } }));
    await select(prepared);
    await screen.findByText('CONTENT BLOCKS');
    expect(mocks.createProject).toHaveBeenCalledExactlyOnceWith('Imported');
    expect(mocks.saveEditor).toHaveBeenCalledExactlyOnceWith(importedId, prepared, importedMetadata.updated_at);
    expect(mocks.openProject).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(mocks.generateText).not.toHaveBeenCalled();
    expect(mocks.generateImage).not.toHaveBeenCalled();
    expect(mocks.deployNetlify).not.toHaveBeenCalled();
    expect(mocks.exportZip).not.toHaveBeenCalled();
  });

  it('rejects an invalid selected file before any project mutation and shows safe bilingual copy', async () => {
    await select({ ...blankEditor('Imported', 'ru'), schema_version: 2 } as unknown as EditorDocument, 'ru');
    expect(await screen.findByRole('alert')).toHaveTextContent('не соответствует формату редактора AURORA v1');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(screen.getByText(/Импорт создаёт новый текстовый проект без AI-запроса/)).toBeInTheDocument();
  });

  it('reports a failed create and does not attempt editor save', async () => {
    mocks.createProject.mockRejectedValue(new ApiError(503));
    await select(blankEditor('Imported', 'en'));
    expect(await screen.findByRole('alert')).toHaveTextContent('Project creation was not confirmed');
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Import prepared site' })).toBeEnabled();
  });

  it('allows only one pending import while the save is unresolved', async () => {
    let finish: ((document: ProjectDocument) => void) | undefined;
    const prepared = blankEditor('Imported', 'en');
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    mocks.saveEditor.mockImplementation(() => new Promise<ProjectDocument>((resolve) => { finish = resolve; }));
    await select(prepared);
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    expect(screen.getByRole('button', { name: 'Import prepared site' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Import prepared site' }));
    expect(mocks.createProject).toHaveBeenCalledTimes(1);
    finish?.({ metadata: importedMetadata, state: { editor: prepared } });
    await screen.findByText('CONTENT BLOCKS');
  });

  it('reports a new project left after save failure and never claims import success', async () => {
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    mocks.saveEditor.mockRejectedValue(new ApiError(409));
    mocks.listProjects.mockResolvedValue([metadata, importedMetadata]);
    await select(blankEditor('Imported', 'en'));
    expect(await screen.findByRole('alert')).toHaveTextContent('a new project may remain');
    expect(mocks.saveEditor).toHaveBeenCalledTimes(1);
    expect(screen.queryByText('CONTENT BLOCKS')).not.toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: 'Imported' })).toBeInTheDocument();
    expect(mocks.deleteProject).not.toHaveBeenCalled();
  });

  it('refuses a mismatched save response instead of opening the workspace', async () => {
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    const altered = blankEditor('Imported', 'en');
    altered.brand.tagline = 'Changed by server';
    mocks.saveEditor.mockResolvedValue({ metadata: importedMetadata, state: { editor: altered } });
    await select(blankEditor('Imported', 'en'));
    expect(await screen.findByRole('alert')).toHaveTextContent('Import is not confirmed');
    expect(screen.queryByText('CONTENT BLOCKS')).not.toBeInTheDocument();
  });

  it('refuses a save response belonging to another project', async () => {
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    const prepared = blankEditor('Imported', 'en');
    mocks.saveEditor.mockResolvedValue({ metadata, state: { editor: prepared } });
    await select(prepared);
    expect(await screen.findByRole('alert')).toHaveTextContent('Import is not confirmed');
    expect(screen.queryByText('CONTENT BLOCKS')).not.toBeInTheDocument();
  });
});

describe('UI-009 direct prepared JSON paste', () => {
  const importedId = '00000000-0000-4000-8000-000000000779';
  const importedMetadata = { ...metadata, project_id: importedId, name: 'Pasted', updated_at: '2026-10-21T01:00:00Z' };

  async function paste(value: string, language: 'ru' | 'en' = 'en') {
    await enter(language);
    fireEvent.change(screen.getByLabelText(language === 'en' ? 'Project name' : 'Название проекта'),
      { target: { value: 'Pasted' } });
    fireEvent.change(screen.getByLabelText(language === 'en' ? 'Paste prepared site JSON' : 'Вставьте JSON подготовленного сайта'),
      { target: { value } });
    fireEvent.click(screen.getByRole('button', {
      name: language === 'en' ? 'Import pasted site' : 'Импортировать вставленный сайт',
    }));
  }

  it('validates and saves pasted P7 as a separate project without AI or asset calls', async () => {
    const prepared = blankEditor('Pasted', 'en');
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    mocks.saveEditor.mockImplementation(async (_id: string, editor: EditorDocument) =>
      ({ metadata: { ...importedMetadata, updated_at: '2026-10-21T02:00:00Z' }, state: { editor } }));
    await paste(JSON.stringify(prepared));
    await screen.findByText('CONTENT BLOCKS');
    expect(mocks.createProject).toHaveBeenCalledExactlyOnceWith('Pasted');
    expect(mocks.saveEditor).toHaveBeenCalledExactlyOnceWith(importedId, prepared, importedMetadata.updated_at);
    expect(mocks.openProject).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(mocks.generateText).not.toHaveBeenCalled();
    expect(mocks.generateImage).not.toHaveBeenCalled();
    expect(mocks.uploadRaster).not.toHaveBeenCalled();
    expect(mocks.deployNetlify).not.toHaveBeenCalled();
  });

  it('rejects invalid pasted JSON before creating a project and leaves it editable', async () => {
    await paste('{ invalid', 'ru');
    expect(await screen.findByRole('alert')).toHaveTextContent('не содержит корректный JSON');
    expect(screen.getByLabelText('Вставьте JSON подготовленного сайта')).toHaveValue('{ invalid');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
  });

  it('applies the existing one MiB UTF-8 byte limit to pasted text', async () => {
    await paste('я'.repeat(524289));
    expect(await screen.findByRole('alert')).toHaveTextContent('no larger than 1 MiB');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
  });

  it('keeps file and paste actions independent and disables empty paste', async () => {
    const fileEditor = blankEditor('File version', 'en');
    await enter();
    expect(screen.getByRole('button', { name: 'Import pasted site' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Pasted' } });
    fireEvent.change(screen.getByLabelText('Prepared site JSON file'), { target: { files: [importFile(fileEditor)] } });
    expect(screen.getByRole('button', { name: 'Import pasted site' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Paste prepared site JSON'), { target: { value: '   ' } });
    expect(screen.getByRole('button', { name: 'Import pasted site' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Import prepared site' }));
    await screen.findByText('CONTENT BLOCKS');
    expect(mocks.saveEditor.mock.calls[0]?.[1]).toEqual(fileEditor);
  });

  it('uses pasted text rather than the selected file when the paste action is chosen', async () => {
    const pastedEditor = blankEditor('Pasted version', 'en');
    const fileEditor = blankEditor('File version', 'en');
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    mocks.saveEditor.mockImplementation(async (_id: string, editor: EditorDocument) =>
      ({ metadata: importedMetadata, state: { editor } }));
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Pasted' } });
    fireEvent.change(screen.getByLabelText('Prepared site JSON file'), { target: { files: [importFile(fileEditor)] } });
    fireEvent.change(screen.getByLabelText('Paste prepared site JSON'),
      { target: { value: JSON.stringify(pastedEditor) } });
    fireEvent.click(screen.getByRole('button', { name: 'Import pasted site' }));
    await screen.findByText('CONTENT BLOCKS');
    expect(mocks.saveEditor.mock.calls[0]?.[1]).toEqual(pastedEditor);
    expect(mocks.createProject).toHaveBeenCalledTimes(1);
  });
});

describe('UI-010 in-app prepared JSON guide', () => {
  it.each(['ru', 'en'] as const)('shows selectable %s guidance without using project actions', async (language) => {
    await enter(language);
    const summary = screen.getByText(language === 'ru'
      ? 'Как подготовить JSON для импорта' : 'How to prepare import JSON');
    const details = summary.closest('details');
    expect(details).not.toHaveAttribute('open');
    fireEvent.click(summary);
    expect(details).toHaveAttribute('open');
    const prompt = screen.getByLabelText(language === 'ru'
      ? 'Шаблон запроса (выделяется при щелчке)' : 'Preparation prompt (click to select)');
    expect(prompt).toHaveAttribute('readonly');
    expect((prompt as HTMLTextAreaElement).value).toContain(`"language": "${language}"`);
    fireEvent.change(screen.getByLabelText(language === 'ru' ? 'Опишите бизнес одним запросом'
      : 'Describe your business in one prompt'), { target: { value: 'PRIVATE BRIEF' } });
    expect((prompt as HTMLTextAreaElement).value).not.toContain('PRIVATE BRIEF');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(mocks.uploadRaster).not.toHaveBeenCalled();
    expect(mocks.deployNetlify).not.toHaveBeenCalled();
  });
});

describe('UI-016 prepared JSON guide copy', () => {
  it.each(['ru', 'en'] as const)('copies only the exact static %s template', async (language) => {
    const copy = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', { clipboard: { writeText: copy } });
    await enter(language);
    fireEvent.change(screen.getByLabelText(language === 'ru' ? 'Название проекта' : 'Project name'),
      { target: { value: 'PRIVATE PROJECT' } });
    fireEvent.change(screen.getByLabelText(language === 'ru' ? 'Опишите бизнес одним запросом'
      : 'Describe your business in one prompt'), { target: { value: 'PRIVATE BRIEF' } });
    fireEvent.change(screen.getByLabelText(language === 'ru' ? 'Вставьте JSON подготовленного сайта'
      : 'Paste prepared site JSON'), { target: { value: 'PRIVATE JSON' } });
    fireEvent.click(screen.getByText(language === 'ru'
      ? 'Как подготовить JSON для импорта' : 'How to prepare import JSON'));
    fireEvent.click(screen.getByRole('button', { name: language === 'ru'
      ? 'Копировать шаблон запроса' : 'Copy preparation prompt' }));
    await waitFor(() => expect(copy).toHaveBeenCalledExactlyOnceWith(preparedSitePrompt(language)));
    expect(copy.mock.calls[0]?.[0]).not.toContain('PRIVATE PROJECT');
    expect(copy.mock.calls[0]?.[0]).not.toContain('PRIVATE BRIEF');
    expect(copy.mock.calls[0]?.[0]).not.toContain('PRIVATE JSON');
    expect(screen.getByRole('status')).toHaveTextContent(language === 'ru'
      ? 'Шаблон скопирован' : 'Preparation prompt copied');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
  });

  it('keeps the prompt selectable and reports a denied clipboard write', async () => {
    vi.stubGlobal('navigator', { clipboard: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } });
    await enter();
    fireEvent.click(screen.getByText('How to prepare import JSON'));
    const prompt = screen.getByLabelText('Preparation prompt (click to select)') as HTMLTextAreaElement;
    fireEvent.click(screen.getByRole('button', { name: 'Copy preparation prompt' }));
    expect(await screen.findByRole('status')).toHaveTextContent(/select the prompt and copy it manually/i);
    expect(prompt).toHaveAttribute('readonly');
    fireEvent.focus(prompt);
    expect(prompt.selectionStart).toBe(0);
    expect(prompt.selectionEnd).toBe(prompt.value.length);
    expect(mocks.createProject).not.toHaveBeenCalled();
  });

  it('reports an unavailable clipboard API without changing the guide', async () => {
    vi.stubGlobal('navigator', {});
    await enter('ru');
    fireEvent.click(screen.getByText('Как подготовить JSON для импорта'));
    const prompt = screen.getByLabelText('Шаблон запроса (выделяется при щелчке)') as HTMLTextAreaElement;
    fireEvent.click(screen.getByRole('button', { name: 'Копировать шаблон запроса' }));
    expect(await screen.findByRole('status')).toHaveTextContent('выделите шаблон и скопируйте вручную');
    expect(prompt.value).toBe(preparedSitePrompt('ru'));
    expect(mocks.createProject).not.toHaveBeenCalled();
  });
});

describe('UI-017 prepared JSON brief copy', () => {
  it.each(['ru', 'en'] as const)('copies one explicit %s brief without mixing other inputs', async (language) => {
    const copy = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', { clipboard: { writeText: copy } });
    await enter(language);
    fireEvent.change(screen.getByLabelText(language === 'ru' ? 'Название проекта' : 'Project name'),
      { target: { value: 'PRIVATE PROJECT' } });
    fireEvent.change(screen.getByLabelText(language === 'ru' ? 'Опишите бизнес одним запросом'
      : 'Describe your business in one prompt'), { target: { value: 'PRIVATE OPENAI PROMPT' } });
    fireEvent.change(screen.getByLabelText(language === 'ru' ? 'Вставьте JSON подготовленного сайта'
      : 'Paste prepared site JSON'), { target: { value: 'PRIVATE JSON' } });
    fireEvent.click(screen.getByText(language === 'ru'
      ? 'Как подготовить JSON для импорта' : 'How to prepare import JSON'));
    const briefLabel = language === 'ru' ? 'ТЗ для внешней подготовки' : 'Brief for external preparation';
    fireEvent.change(screen.getByLabelText(briefLabel), { target: { value: '  Approved brief\nsecond line  ' } });
    fireEvent.click(screen.getByRole('button', { name: language === 'ru'
      ? 'Копировать шаблон с ТЗ' : 'Copy prompt with brief' }));
    const expected = preparedSitePromptWithBrief(language, '  Approved brief\nsecond line  ');
    await waitFor(() => expect(copy).toHaveBeenCalledExactlyOnceWith(expected));
    expect(copy.mock.calls[0]?.[0]).not.toContain('PRIVATE PROJECT');
    expect(copy.mock.calls[0]?.[0]).not.toContain('PRIVATE OPENAI PROMPT');
    expect(copy.mock.calls[0]?.[0]).not.toContain('PRIVATE JSON');
    expect(screen.getByRole('status')).toHaveTextContent(language === 'ru'
      ? 'Шаблон с ТЗ скопирован' : 'Prompt with brief copied');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
  });

  it('keeps the static copy free of the dedicated brief', async () => {
    const copy = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', { clipboard: { writeText: copy } });
    await enter();
    fireEvent.click(screen.getByText('How to prepare import JSON'));
    fireEvent.change(screen.getByLabelText('Brief for external preparation'),
      { target: { value: 'PRIVATE EXTERNAL BRIEF' } });
    fireEvent.click(screen.getByRole('button', { name: 'Copy preparation prompt' }));
    await waitFor(() => expect(copy).toHaveBeenCalledExactlyOnceWith(preparedSitePrompt('en')));
    expect(copy.mock.calls[0]?.[0]).not.toContain('PRIVATE EXTERNAL BRIEF');
  });

  it('enforces the 8-KiB UTF-8 boundary and rejects malformed Unicode', async () => {
    await enter();
    fireEvent.click(screen.getByText('How to prepare import JSON'));
    const brief = screen.getByLabelText('Brief for external preparation');
    const action = screen.getByRole('button', { name: 'Copy prompt with brief' });
    expect(action).toBeDisabled();
    fireEvent.change(brief, { target: { value: 'é'.repeat(4096) } });
    expect(action).toBeEnabled();
    fireEvent.change(brief, { target: { value: 'é'.repeat(4097) } });
    expect(action).toBeDisabled();
    fireEvent.change(brief, { target: { value: '\ud800' } });
    expect(action).toBeDisabled();
  });

  it('retains the brief and reports clipboard denial without project side effects', async () => {
    vi.stubGlobal('navigator', { clipboard: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } });
    await enter('ru');
    fireEvent.click(screen.getByText('Как подготовить JSON для импорта'));
    const brief = screen.getByLabelText('ТЗ для внешней подготовки') as HTMLTextAreaElement;
    fireEvent.change(brief, { target: { value: 'Разрешённое ТЗ' } });
    fireEvent.click(screen.getByRole('button', { name: 'Копировать шаблон с ТЗ' }));
    expect(await screen.findByRole('status')).toHaveTextContent('скопируйте вручную');
    expect(brief.value).toBe('Разрешённое ТЗ');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
  });
});

describe('UI-012 project creation path clarity', () => {
  it.each(['ru', 'en'] as const)('separates the three %s paths without triggering any action', async (language) => {
    await enter(language);
    const ai = screen.getByRole('region', { name: language === 'ru' ? 'Создать с OpenAI' : 'Generate with OpenAI' });
    const blank = screen.getByRole('region', { name: language === 'ru' ? 'Начать вручную' : 'Start manually' });
    const imported = screen.getByRole('region', { name: language === 'ru'
      ? 'Импортировать подготовленный сайт' : 'Import a prepared site' });
    expect(ai).toHaveTextContent(language === 'ru' ? 'Нужен ключ OpenAI' : 'OpenAI key required');
    expect(ai).toHaveTextContent(language === 'ru' ? 'Запрос к провайдеру может быть платным'
      : 'The provider request may incur a charge');
    expect(blank).toHaveTextContent(language === 'ru' ? 'Без ключа OpenAI' : 'No OpenAI key required');
    expect(imported).toHaveTextContent(language === 'ru' ? 'у внешнего инструмента могут быть свои условия и расходы'
      : 'that external tool may have its own terms and costs');
    expect(within(ai).getByRole('button', { name: language === 'ru' ? 'Создать из запроса' : 'Generate from prompt' })).toBeDisabled();
    expect(within(blank).getByRole('button', { name: language === 'ru' ? 'Создать проект' : 'Create project' })).toBeDisabled();
    expect(within(imported).getByRole('button', { name: language === 'ru'
      ? 'Импортировать подготовленный сайт' : 'Import prepared site' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText(language === 'ru' ? 'Название проекта' : 'Project name'),
      { target: { value: 'Studio' } });
    expect(within(blank).getByRole('button', { name: language === 'ru' ? 'Создать проект' : 'Create project' })).toBeEnabled();
    expect(within(ai).getByRole('button', { name: language === 'ru' ? 'Создать из запроса' : 'Generate from prompt' })).toBeDisabled();
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.uploadRaster).not.toHaveBeenCalled();
    expect(mocks.deployNetlify).not.toHaveBeenCalled();
  });
});

describe('UI-013 prepared JSON drop selection', () => {
  it('selects one dropped file but imports only after the explicit file action', async () => {
    const prepared = blankEditor('Imported', 'en');
    const importedId = '00000000-0000-4000-8000-000000000778';
    const importedMetadata = { ...metadata, project_id: importedId, name: 'Imported' };
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    mocks.saveEditor.mockImplementation(async (_id: string, editor: EditorDocument) =>
      ({ metadata: importedMetadata, state: { editor } }));
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Imported' } });
    const zone = screen.getByRole('region', { name: 'JSON file selection area' });
    expect(zone).toHaveTextContent('Dropping alone does not create a project');
    fireEvent.dragEnter(zone);
    expect(zone).toHaveClass('dragging');
    expect(mocks.createProject).not.toHaveBeenCalled();
    fireEvent.drop(zone, { dataTransfer: { files: [importFile(prepared)] } });
    expect(zone).not.toHaveClass('dragging');
    expect(within(zone).getByText('Selected file: prepared.json')).toBeInTheDocument();
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Import pasted site' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Import prepared site' }));
    await screen.findByText('CONTENT BLOCKS');
    expect(mocks.createProject).toHaveBeenCalledExactlyOnceWith('Imported');
    expect(mocks.saveEditor).toHaveBeenCalledExactlyOnceWith(importedId, prepared, importedMetadata.updated_at);
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(mocks.uploadRaster).not.toHaveBeenCalled();
    expect(mocks.deployNetlify).not.toHaveBeenCalled();
  });

  it('rejects multiple dropped files without replacing a previous picker selection', async () => {
    await enter('ru');
    fireEvent.change(screen.getByLabelText('Название проекта'), { target: { value: 'Импорт' } });
    const zone = screen.getByRole('region', { name: 'Область выбора JSON-файла' });
    fireEvent.change(within(zone).getByLabelText('JSON-файл подготовленного сайта'),
      { target: { files: [new File(['old'], 'old.json')] } });
    fireEvent.drop(zone, { dataTransfer: { files: [new File(['one'], 'one.json'),
      new File(['two'], 'two.json')] } });
    fireEvent.drop(zone, { dataTransfer: { files: [] } });
    expect(within(zone).getByText('Выбран файл: old.json')).toBeInTheDocument();
    expect(within(zone).getByRole('alert')).toHaveTextContent('Предыдущий выбор сохранён');
    expect(screen.getByRole('button', { name: 'Импортировать подготовленный сайт' })).toBeEnabled();
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
  });

  it('runs the existing strict validator on an explicitly imported dropped file', async () => {
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Imported' } });
    fireEvent.drop(screen.getByRole('region', { name: 'JSON file selection area' }),
      { dataTransfer: { files: [new File(['not JSON'], 'misleading.json', { type: 'application/json' })] } });
    fireEvent.click(screen.getByRole('button', { name: 'Import prepared site' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('does not contain valid JSON');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
  });

  it('keeps a dropped file separate from the pasted JSON action', async () => {
    const pasted = blankEditor('Pasted', 'en');
    const importedId = '00000000-0000-4000-8000-000000000779';
    const importedMetadata = { ...metadata, project_id: importedId, name: 'Pasted' };
    mocks.createProject.mockResolvedValue({ metadata: importedMetadata, state: {} });
    mocks.saveEditor.mockImplementation(async (_id: string, editor: EditorDocument) =>
      ({ metadata: importedMetadata, state: { editor } }));
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Pasted' } });
    fireEvent.drop(screen.getByRole('region', { name: 'JSON file selection area' }),
      { dataTransfer: { files: [new File(['not JSON'], 'invalid.json')] } });
    fireEvent.change(screen.getByLabelText('Paste prepared site JSON'),
      { target: { value: JSON.stringify(pasted) } });
    fireEvent.click(screen.getByRole('button', { name: 'Import pasted site' }));
    await screen.findByText('CONTENT BLOCKS');
    expect(mocks.saveEditor).toHaveBeenCalledExactlyOnceWith(importedId, pasted, importedMetadata.updated_at);
  });
});

describe('UI-014 explicit project creation', () => {
  it('does not create a blank project when Enter is pressed in the shared name field', async () => {
    await enter();
    const keyboard = userEvent.setup();
    fireEvent.change(screen.getByLabelText('Paste prepared site JSON'), { target: { value: '{}' } });
    await keyboard.type(screen.getByLabelText('Project name'), 'Prepared site{Enter}');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(screen.getByRole('region', { name: 'Import a prepared site' })).toBeInTheDocument();
  });

  it('creates a blank project through focused keyboard activation of its own button', async () => {
    await enter();
    const keyboard = userEvent.setup();
    await keyboard.type(screen.getByLabelText('Project name'), '  Studio  ');
    const create = screen.getByRole('button', { name: 'Create project' });
    create.focus();
    await keyboard.keyboard('{Enter}');
    await waitFor(() => expect(mocks.createProject).toHaveBeenCalledExactlyOnceWith('Studio'));
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
  });
});

describe('UI-015 prepared JSON selection clear', () => {
  it('clears a picker selection and permits the same file to be selected again', async () => {
    await enter();
    const user = userEvent.setup();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Imported' } });
    const input = screen.getByLabelText('Prepared site JSON file') as HTMLInputElement;
    const selected = importFile(blankEditor('Imported', 'en'));
    expect(screen.queryByRole('button', { name: 'Clear selected file' })).not.toBeInTheDocument();
    await user.upload(input, selected);
    expect(screen.getByText('Selected file: prepared.json')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Import prepared site' })).toBeEnabled();
    await user.click(screen.getByRole('button', { name: 'Clear selected file' }));
    expect(input.value).toBe('');
    expect(screen.queryByText('Selected file: prepared.json')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Clear selected file' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Import prepared site' })).toBeDisabled();
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    await user.upload(input, selected);
    expect(screen.getByText('Selected file: prepared.json')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Import prepared site' })).toBeEnabled();
    expect(input.value).not.toBe('');
    fireEvent.drop(screen.getByRole('region', { name: 'JSON file selection area' }),
      { dataTransfer: { files: [new File(['replacement'], 'replacement.json')] } });
    expect(input.value).toBe('');
    expect(screen.getByText('Selected file: replacement.json')).toBeInTheDocument();
    expect(mocks.createProject).not.toHaveBeenCalled();
  });

  it('clears a dropped file without changing the pasted JSON path or project name', async () => {
    await enter('ru');
    fireEvent.change(screen.getByLabelText('Название проекта'), { target: { value: 'Импорт' } });
    const pasted = screen.getByLabelText('Вставьте JSON подготовленного сайта') as HTMLTextAreaElement;
    fireEvent.change(pasted, { target: { value: '{}' } });
    const zone = screen.getByRole('region', { name: 'Область выбора JSON-файла' });
    fireEvent.drop(zone, { dataTransfer: { files: [new File(['not JSON'], 'wrong.json')] } });
    expect(within(zone).getByText('Выбран файл: wrong.json')).toBeInTheDocument();
    fireEvent.drop(zone, { dataTransfer: { files: [] } });
    expect(within(zone).getByRole('alert')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Снять выбор файла' }));
    expect(within(zone).queryByText('Выбран файл: wrong.json')).not.toBeInTheDocument();
    expect(within(zone).queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Импортировать подготовленный сайт' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Импортировать вставленный сайт' })).toBeEnabled();
    expect((screen.getByLabelText('Название проекта') as HTMLInputElement).value).toBe('Импорт');
    expect(pasted.value).toBe('{}');
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
  });

  it('does not clear a staged file while its explicit import is in progress', async () => {
    let finishCreate: ((document: ProjectDocument) => void) | undefined;
    mocks.createProject.mockImplementation(() => new Promise<ProjectDocument>((resolve) => {
      finishCreate = resolve;
    }));
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Studio' } });
    fireEvent.change(screen.getByLabelText('Prepared site JSON file'),
      { target: { files: [importFile(blankEditor('Studio', 'en'))] } });
    fireEvent.click(screen.getByRole('button', { name: 'Import prepared site' }));
    await waitFor(() => expect(mocks.createProject).toHaveBeenCalledTimes(1));
    expect(screen.getByRole('button', { name: 'Clear selected file' })).toBeDisabled();
    expect(screen.getByText('Selected file: prepared.json')).toBeInTheDocument();
    expect(finishCreate).toBeDefined();
    finishCreate?.(empty);
    await screen.findByText('CONTENT BLOCKS');
  });
});

describe('UI-018 direct prepared JSON clear', () => {
  it('clears only pasted JSON and preserves adjacent project-path inputs', async () => {
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Imported' } });
    fireEvent.change(screen.getByLabelText('Describe your business in one prompt'),
      { target: { value: 'Independent AI path' } });
    fireEvent.change(screen.getByLabelText('Prepared site JSON file'),
      { target: { files: [importFile(blankEditor('File version', 'en'))] } });
    const zone = screen.getByRole('region', { name: 'JSON file selection area' });
    fireEvent.drop(zone, { dataTransfer: { files: [] } });
    fireEvent.click(screen.getByText('How to prepare import JSON'));
    fireEvent.change(screen.getByLabelText('Brief for external preparation'),
      { target: { value: 'External preparation brief' } });
    vi.stubGlobal('navigator', { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } });
    fireEvent.click(screen.getByRole('button', { name: 'Copy preparation prompt' }));
    await screen.findByText('Preparation prompt copied.');
    const pasted = screen.getByLabelText('Paste prepared site JSON') as HTMLTextAreaElement;
    fireEvent.change(pasted, { target: { value: '{}' } });

    fireEvent.click(screen.getByRole('button', { name: 'Clear pasted JSON' }));

    expect(pasted).toHaveValue('');
    expect(screen.queryByRole('button', { name: 'Clear pasted JSON' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Import pasted site' })).toBeDisabled();
    expect(screen.getByLabelText('Project name')).toHaveValue('Imported');
    expect(screen.getByLabelText('Describe your business in one prompt')).toHaveValue('Independent AI path');
    expect(screen.getByText('Selected file: prepared.json')).toBeInTheDocument();
    expect(within(zone).getByRole('alert')).toBeInTheDocument();
    expect(screen.getByLabelText('Brief for external preparation')).toHaveValue('External preparation brief');
    expect(screen.getByText('Preparation prompt copied.')).toBeInTheDocument();
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    expect(mocks.uploadRaster).not.toHaveBeenCalled();
    expect(mocks.deployNetlify).not.toHaveBeenCalled();
  });

  it('offers a Russian clear action for whitespace without enabling import', async () => {
    await enter('ru');
    const pasted = screen.getByLabelText('Вставьте JSON подготовленного сайта');
    expect(screen.queryByRole('button', { name: 'Очистить вставленный JSON' })).not.toBeInTheDocument();
    fireEvent.change(pasted, { target: { value: '   ' } });
    expect(screen.getByRole('button', { name: 'Импортировать вставленный сайт' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Очистить вставленный JSON' }));
    expect(pasted).toHaveValue('');
    expect(screen.queryByRole('button', { name: 'Очистить вставленный JSON' })).not.toBeInTheDocument();
  });

  it('does not clear pasted JSON while another project operation is busy', async () => {
    let finishCreate: ((document: ProjectDocument) => void) | undefined;
    mocks.createProject.mockImplementation(() => new Promise<ProjectDocument>((resolve) => {
      finishCreate = resolve;
    }));
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Studio' } });
    const pasted = screen.getByLabelText('Paste prepared site JSON');
    fireEvent.change(pasted, { target: { value: '{}' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create project' }));
    await waitFor(() => expect(mocks.createProject).toHaveBeenCalledTimes(1));
    const clear = screen.getByRole('button', { name: 'Clear pasted JSON' });
    expect(clear).toBeDisabled();
    fireEvent.click(clear);
    expect(pasted).toHaveValue('{}');
    expect(finishCreate).toBeDefined();
    finishCreate?.(empty);
    await screen.findByRole('button', { name: 'Start blank site' });
  });
});

describe('workspace flow', () => {
  it('chooses RU/EN, creates an empty project, then explicitly initializes P7', async () => {
    await enter('ru');
    expect(mocks.savePreferences).toHaveBeenCalledTimes(2);
    expect(mocks.savePreferences.mock.calls[0]?.[1]).toBe('a'.repeat(64));
    expect(mocks.savePreferences.mock.calls[0]?.[0]).toMatchObject({ language: 'ru', onboarding_completed: false });
    expect(mocks.savePreferences.mock.calls[1]?.[0]).toMatchObject({ language: 'ru', onboarding_completed: true });
    const input = screen.getByLabelText('Название проекта');
    fireEvent.change(input, { target: { value: 'Кофейня' } });
    fireEvent.click(screen.getByRole('button', { name: 'Создать проект' }));
    const blank = await screen.findByRole('button', { name: 'Начать с пустого сайта' });
    expect(mocks.createProject).toHaveBeenCalledWith('Кофейня');
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    fireEvent.click(blank);
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    const [projectId, editor, stamp] = mocks.saveEditor.mock.calls[0] as [string, EditorDocument, string];
    expect(projectId).toBe(id);
    expect(stamp).toBe(metadata.updated_at);
    expect(editor.language).toBe('ru');
    expect(editor.pages[0]?.sections[0]?.heading).toBe('О нас');
  });

  it('opens an existing project, collapses panels and loads a sandboxed saved preview', async () => {
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    fireEvent.click(screen.getByRole('button', { name: 'Toggle Pages' }));
    expect(screen.queryByRole('button', { name: 'Add page' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Toggle Inspector / AI' }));
    expect(screen.queryByText('TEXT ASSIST')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Preview' }));
    const frame = await screen.findByTitle('Preview');
    expect(frame).toHaveAttribute('sandbox', 'allow-same-origin');
    expect(frame.getAttribute('src')).toContain(`/api/v1/projects/${id}/preview/index.html`);
    expect(frame.getAttribute('sandbox')).not.toContain('allow-scripts');
    fireEvent.click(screen.getByRole('button', { name: 'Mobile' }));
    expect(frame.parentElement).toHaveClass('mobile');
  });

  it('retains the draft after a 409 and does not automatically retry', async () => {
    mocks.saveEditor.mockRejectedValue(new ApiError(409));
    vi.stubGlobal('confirm', vi.fn(() => true));
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    const tagline = screen.getByLabelText('Tagline');
    fireEvent.change(tagline, { target: { value: 'New tagline' } });
    fireEvent.blur(tagline);
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    expect(await screen.findByText('Unsaved changes')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Export & deploy' }));
    expect(screen.getByText('CONTENT BLOCKS')).toBeInTheDocument();
    expect(mocks.saveEditor).toHaveBeenCalledTimes(1);
  });

  it('allows a corrected confirmed edit after a rejected 400', async () => {
    mocks.saveEditor.mockRejectedValueOnce(new ApiError(400))
      .mockImplementationOnce(async (_projectId: string, next: EditorDocument) => withEditor(next));
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    const tagline = screen.getByLabelText('Tagline');
    fireEvent.change(tagline, { target: { value: 'Bad' } }); fireEvent.blur(tagline);
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    const corrected = screen.getByLabelText('Tagline');
    fireEvent.change(corrected, { target: { value: 'Corrected' } }); fireEvent.blur(corrected);
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(2));
    expect((mocks.saveEditor.mock.calls[1]?.[1] as EditorDocument).brand.tagline).toBe('Corrected');
  });

  it('never retains a submitted credential in the visible input', async () => {
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Settings' }));
    const key = await screen.findByLabelText('OpenAI key');
    await userEvent.type(key, 'test-secret');
    const group = key.closest('.setting-secret');
    expect(group).not.toBeNull();
    fireEvent.click(within(group as HTMLElement).getByRole('button', { name: 'Save key' }));
    await waitFor(() => expect(mocks.setCredential).toHaveBeenCalledWith('openai_api_key', 'test-secret'));
    await waitFor(() => expect(key).toHaveValue(''));
    expect(screen.queryByText('test-secret')).not.toBeInTheDocument();
  });

  it('keeps unsupported editor state untouched and never offers blank overwrite', async () => {
    mocks.openProject.mockResolvedValue({ metadata, state: { editor: { schema_version: 2 } } });
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    expect(await screen.findByText(/unsupported or damaged/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Start blank site' })).not.toBeInTheDocument();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
  });

  it('requires the exact project name before deletion', async () => {
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Delete project' }));
    const dialog = screen.getByRole('dialog', { name: 'Delete project' });
    const button = within(dialog).getByRole('button', { name: 'Delete project' });
    expect(button).toBeDisabled();
    fireEvent.change(within(dialog).getByLabelText('Type the exact project name to delete'), { target: { value: 'Wrong' } });
    expect(button).toBeDisabled();
    fireEvent.change(within(dialog).getByLabelText('Type the exact project name to delete'), { target: { value: 'Studio' } });
    fireEvent.click(button);
    await waitFor(() => expect(mocks.deleteProject).toHaveBeenCalledWith(id));
  });

  it('serializes confirmed edits and uses the preceding successful timestamp', async () => {
    let finishFirst: ((value: ProjectDocument) => void) | undefined;
    mocks.saveEditor.mockImplementationOnce(() => new Promise<ProjectDocument>((resolve) => { finishFirst = resolve; }))
      .mockImplementationOnce(async (_projectId: string, next: EditorDocument) => ({
        metadata: { ...metadata, updated_at: '2026-10-09T04:00:00Z' }, state: { editor: next },
      }));
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    const tagline = screen.getByLabelText('Tagline');
    fireEvent.change(tagline, { target: { value: 'First' } }); fireEvent.blur(tagline);
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    const brand = screen.getByLabelText('Brand name');
    fireEvent.change(brand, { target: { value: 'Second' } }); fireEvent.blur(brand);
    expect(mocks.saveEditor).toHaveBeenCalledTimes(1);
    const firstEditor = mocks.saveEditor.mock.calls[0]?.[1] as EditorDocument;
    finishFirst?.({ metadata: { ...metadata, updated_at: '2026-10-09T03:00:00Z' }, state: { editor: firstEditor } });
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(2));
    expect(mocks.saveEditor.mock.calls[1]?.[2]).toBe('2026-10-09T03:00:00Z');
    expect((mocks.saveEditor.mock.calls[1]?.[1] as EditorDocument).brand.name).toBe('Second');
  });

  it('adds pages and sections without changing the immutable index homepage', async () => {
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    expect(screen.getByRole('button', { name: 'Delete Studio' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Page name'), { target: { value: 'Services' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add page' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    const added = mocks.saveEditor.mock.calls[0]?.[1] as EditorDocument;
    expect(added.pages.map((page) => page.slug)).toEqual(['index', 'page-1']);
    fireEvent.change(screen.getByLabelText('Section heading'), { target: { value: 'What we do' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add section' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(2));
    const second = mocks.saveEditor.mock.calls[1]?.[1] as EditorDocument;
    expect(second.pages[1]?.sections[0]?.heading).toBe('What we do');
    expect(second.pages[0]?.slug).toBe('index');
  });

  it('applies paid text assistance only after explicit review', async () => {
    mocks.generateText.mockResolvedValue({ job_id: id, status: 'completed', result: { response_id: 'r', model: 'm', output_text: 'Suggested copy' }, failure: null });
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    fireEvent.change(screen.getByLabelText('What should change in the selected block?'), { target: { value: 'Rewrite' } });
    expect(mocks.generateText).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Generate suggestion' }));
    expect(await screen.findByText('Suggested copy')).toBeInTheDocument();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Apply to selected block' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    expect((mocks.saveEditor.mock.calls[0]?.[1] as EditorDocument).pages[0]?.sections[0]?.body).toBe('Suggested copy');
  });

  it('uploads raster then dereferences before P1 deletion', async () => {
    const path = `assets/${'a'.repeat(64)}.png`;
    mocks.uploadRaster.mockResolvedValue(path);
    mocks.deleteRaster.mockResolvedValue(undefined);
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    const upload = document.querySelector('.section-card input[type="file"]') as HTMLInputElement;
    fireEvent.change(upload, { target: { files: [new File(['png'], 'photo.png', { type: 'image/png' })] } });
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    expect((mocks.saveEditor.mock.calls[0]?.[1] as EditorDocument).pages[0]?.sections[0]?.image_path).toBe(path);
    const sectionCard = document.querySelector('.section-card') as HTMLElement;
    fireEvent.click(within(sectionCard).getByRole('button', { name: 'Remove image' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(mocks.deleteRaster).toHaveBeenCalledWith(id, `${'a'.repeat(64)}.png`));
    expect((mocks.saveEditor.mock.calls[1]?.[1] as EditorDocument).pages[0]?.sections[0]?.image_path).toBeNull();
  });
});

describe('one-prompt project draft', () => {
  it('reopens an idle guided plan from a saved editor; skipped slots remain available next session', async () => {
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    fireEvent.click(screen.getByRole('button', { name: 'Complete project images' }));
    expect(await screen.findByRole('button', { name: 'Review image plan' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    fireEvent.click(screen.getByRole('button', { name: 'Skip this image' }));
    expect(screen.getByText('Studio / About', { selector: 'h2' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Open workspace' }));
    await screen.findByText('CONTENT BLOCKS');
    fireEvent.click(screen.getByRole('button', { name: 'Complete project images' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Review image plan' }));
    expect(screen.getByText('Create a brand logo for "Studio". Tagline: "". Language: en.')).toBeInTheDocument();
    expect(mocks.generateImage).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Open workspace' }));
    fireEvent.click(screen.getByRole('button', { name: 'Export & deploy' }));
    expect(await screen.findByRole('button', { name: 'Download site ZIP' })).toBeInTheDocument();
  });

  it('requires per-attempt confirmation, reviews unsaved text, then accepts with the source timestamp', async () => {
    const confirm = vi.fn(() => false);
    vi.stubGlobal('confirm', confirm);
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Studio' } });
    fireEvent.change(screen.getByLabelText('Describe your business in one prompt'),
      { target: { value: '  Make a studio site  ' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate from prompt' }));
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).not.toHaveBeenCalled();
    confirm.mockReturnValue(true);
    fireEvent.click(screen.getByRole('button', { name: 'Generate from prompt' }));
    expect(await screen.findByRole('heading', { name: 'Review draft' })).toBeInTheDocument();
    expect(mocks.createProject).toHaveBeenCalledWith('Studio');
    expect(mocks.generateProjectDraft).toHaveBeenCalledWith(id, '  Make a studio site  ', 'en', 'gpt-5.6-terra', metadata.updated_at);
    expect(mocks.createProject.mock.invocationCallOrder[0]).toBeLessThan(mocks.generateProjectDraft.mock.invocationCallOrder[0] ?? 0);
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(screen.getByText('Not saved')).toBeInTheDocument();
    expect(screen.getByText('About')).toBeInTheDocument();
    expect(screen.queryByTitle('Preview')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Accept and save' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    expect(mocks.saveEditor).toHaveBeenCalledWith(id, expect.objectContaining({ schema_version: 1 }), metadata.updated_at);
    expect(await screen.findByRole('heading', { name: 'Complete project images' })).toBeInTheDocument();
    expect(mocks.generateImage).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Open workspace' }));
    expect(await screen.findByText('CONTENT BLOCKS')).toBeInTheDocument();
  });

  it('keeps the created empty project on generation error and offers deliberate retry', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true));
    mocks.generateProjectDraft.mockRejectedValue(new ApiError(503));
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Studio' } });
    fireEvent.change(screen.getByLabelText('Describe your business in one prompt'), { target: { value: 'A studio' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate from prompt' }));
    await waitFor(() => expect(mocks.generateProjectDraft).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole('button', { name: 'Generate from prompt' })).toBeInTheDocument();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.deleteProject).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Workspace' }));
    expect(await screen.findByRole('button', { name: 'Start blank site' })).toBeInTheDocument();
  });

  it('shows a terminal failure without saving and requires another click to retry', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true));
    mocks.generateProjectDraft.mockResolvedValueOnce({ job_id: id, status: 'failed',
      source_updated_at: metadata.updated_at, editor: null,
      failure: { category: 'rate_limited', message: 'Safe message', retryable: true } });
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Studio' } });
    fireEvent.change(screen.getByLabelText('Describe your business in one prompt'), { target: { value: 'A studio' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate from prompt' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('rate_limited');
    expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument();
    expect(mocks.generateProjectDraft).toHaveBeenCalledTimes(1);
    expect(mocks.saveEditor).not.toHaveBeenCalled();
  });

  it('retains the candidate after a 409 and never rebases its acceptance timestamp', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true));
    mocks.saveEditor.mockRejectedValue(new ApiError(409));
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Studio' } });
    fireEvent.change(screen.getByLabelText('Describe your business in one prompt'), { target: { value: 'A studio' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate from prompt' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Accept and save' }));
    expect(await screen.findByText(/automatic overwrite is blocked/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Accept and save' })).toBeDisabled();
    expect(mocks.saveEditor).toHaveBeenCalledTimes(1);
    expect(mocks.saveEditor.mock.calls[0]?.[2]).toBe(metadata.updated_at);
    fireEvent.click(screen.getByRole('button', { name: 'Workspace' }));
    expect(await screen.findByRole('button', { name: 'Start blank site' })).toBeInTheDocument();
    expect(mocks.saveEditor).toHaveBeenCalledTimes(1);
  });

  it('generates from an existing empty project without creating another', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true));
    mocks.openProject.mockResolvedValue(empty);
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('NEW WORKSPACE');
    const generate = screen.getByRole('button', { name: 'Generate from prompt' });
    await waitFor(() => expect(generate).toBeEnabled());
    fireEvent.click(generate);
    fireEvent.change(await screen.findByLabelText('Describe your business in one prompt'), { target: { value: 'Studio site' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate from prompt' }));
    expect(await screen.findByRole('heading', { name: 'Review draft' })).toBeInTheDocument();
    expect(mocks.createProject).not.toHaveBeenCalled();
    expect(mocks.generateProjectDraft).toHaveBeenCalledTimes(1);
  });

  it('shows one honest pending state and warns on pending and unaccepted candidate unload', async () => {
    let finish: ((value: unknown) => void) | undefined;
    mocks.generateProjectDraft.mockImplementation(() => new Promise((resolve) => { finish = resolve; }));
    const confirm = vi.fn(() => true);
    vi.stubGlobal('confirm', confirm);
    await enter();
    fireEvent.change(screen.getByLabelText('Project name'), { target: { value: 'Studio' } });
    fireEvent.change(screen.getByLabelText('Describe your business in one prompt'), { target: { value: 'A studio' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate from prompt' }));
    expect(await screen.findByText('Generating one draft…')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Projects' })).toBeDisabled();
    expect(screen.queryByText('Generating images')).not.toBeInTheDocument();
    const pendingUnload = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(pendingUnload);
    expect(pendingUnload.defaultPrevented).toBe(true);
    expect(mocks.generateProjectDraft).toHaveBeenCalledTimes(1);
    finish?.({ job_id: id, status: 'completed', source_updated_at: metadata.updated_at,
      editor: blankEditor('Studio', 'en'), failure: null });
    expect(await screen.findByRole('heading', { name: 'Review draft' })).toBeInTheDocument();
    const candidateUnload = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(candidateUnload);
    expect(candidateUnload.defaultPrevented).toBe(true);
    confirm.mockReturnValue(false);
    fireEvent.click(screen.getByRole('button', { name: 'Projects' }));
    await waitFor(() => expect(confirm).toHaveBeenCalledTimes(2));
    expect(screen.getByRole('heading', { name: 'Review draft' })).toBeInTheDocument();
    confirm.mockReturnValue(true);
    fireEvent.click(screen.getByRole('button', { name: 'Discard draft' }));
    expect(await screen.findByRole('button', { name: 'Start blank site' })).toBeInTheDocument();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.deleteProject).not.toHaveBeenCalled();
  });

  it('keeps RU language through request and candidate review without browser storage', async () => {
    const storage = vi.spyOn(Storage.prototype, 'setItem');
    mocks.generateProjectDraft.mockResolvedValue({ job_id: id, status: 'completed',
      source_updated_at: metadata.updated_at, editor: blankEditor('Студия', 'ru'), failure: null });
    vi.stubGlobal('confirm', vi.fn(() => true));
    await enter('ru');
    fireEvent.change(screen.getByLabelText('Название проекта'), { target: { value: 'Студия' } });
    fireEvent.change(screen.getByLabelText('Опишите бизнес одним запросом'), { target: { value: 'Сайт студии' } });
    fireEvent.click(screen.getByRole('button', { name: 'Создать из запроса' }));
    expect(await screen.findByRole('heading', { name: 'Просмотр черновика' })).toBeInTheDocument();
    expect(mocks.generateProjectDraft).toHaveBeenCalledWith(id, 'Сайт студии', 'ru', 'gpt-5.6-terra', metadata.updated_at);
    expect(storage).not.toHaveBeenCalled();
    storage.mockRestore();
  });

  it('uses the saved image model and locks workspace navigation while an image is pending or unreviewed', async () => {
    let finish: ((result: unknown) => void) | undefined;
    mocks.generateImage.mockImplementation(() => new Promise((resolve) => { finish = resolve; }));
    vi.stubGlobal('confirm', vi.fn(() => true));
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Settings' }));
    const model = await screen.findByLabelText('OpenAI image model');
    expect(model).toHaveValue('gpt-image-2');
    fireEvent.change(model, { target: { value: 'custom-image-model' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save settings' }));
    await waitFor(() => expect(mocks.savePreferences).toHaveBeenCalledTimes(3));
    fireEvent.click(screen.getByRole('button', { name: 'Projects' }));
    await screen.findByRole('heading', { name: 'Projects' });
    fireEvent.click(screen.getByRole('button', { name: 'Open' }));
    await screen.findByText('CONTENT BLOCKS');
    const generate = screen.getAllByRole('button', { name: 'Generate image' });
    fireEvent.click(generate[generate.length - 1]!);
    const dialog = screen.getByRole('dialog', { name: 'Generate image' });
    expect(screen.getByRole('button', { name: 'Export & deploy' })).toBeDisabled();
    expect(document.querySelector('.workspace .canvas')).toHaveAttribute('inert');
    fireEvent.change(within(dialog).getByLabelText('Describe the image'), { target: { value: 'Studio logo' } });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Generate image' }));
    await waitFor(() => expect(mocks.generateImage).toHaveBeenCalledWith(id, 'Studio logo', 'custom-image-model', '2026-10-09T02:00:00Z'));
    expect(screen.getByRole('button', { name: 'Projects' })).toBeDisabled();
    const unload = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(unload);
    expect(unload.defaultPrevented).toBe(true);
    finish?.({ job_id: id, status: 'completed', source_updated_at: '2026-10-09T02:00:00Z',
      asset_path: `assets/${'a'.repeat(64)}.png`, failure: null });
    await screen.findByText('Stored in project, not attached');
    expect(screen.getByRole('button', { name: 'Settings' })).toBeDisabled();
    fireEvent.click(within(dialog).getByRole('button', { name: 'Discard image' }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Settings' })).toBeEnabled());
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.deleteRaster).not.toHaveBeenCalled();
  });
});

describe('persistent preferences composition', () => {
  it('reopens saved language and models without automatic onboarding and displays the server path read-only', async () => {
    const storage = vi.spyOn(Storage.prototype, 'setItem');
    mocks.getPreferences.mockResolvedValue({ preferences: {
      schema_version: 1, language: 'ru', general_model: 'saved-general', image_model: 'saved-image',
      onboarding_completed: true,
    }, revision: 'a'.repeat(64), projects_directory: 'C:\\Projects' });
    render(<App />);
    expect(await screen.findByRole('heading', { name: 'Проекты' })).toBeInTheDocument();
    expect(screen.queryByRole('dialog', { name: 'AURORA onboarding' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Настройки' }));
    expect(await screen.findByLabelText('Модель OpenAI')).toHaveValue('saved-general');
    expect(screen.getByLabelText('Модель изображений OpenAI')).toHaveValue('saved-image');
    expect(screen.getByText('C:\\Projects').tagName).toBe('OUTPUT');
    fireEvent.change(screen.getByLabelText('Модель OpenAI'), { target: { value: ' ' } });
    expect(screen.getByRole('button', { name: 'Сохранить настройки' })).toBeDisabled();
    expect(mocks.savePreferences).not.toHaveBeenCalled();
    expect(storage).not.toHaveBeenCalled();
    storage.mockRestore();
  });

  it('uses the persisted general model for a later confirmed generation', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true));
    mocks.getPreferences.mockResolvedValue({ preferences: {
      schema_version: 1, language: 'en', general_model: 'saved-general', image_model: 'gpt-image-2',
      onboarding_completed: true,
    }, revision: 'a'.repeat(64), projects_directory: 'C:\\Projects' });
    render(<App />);
    fireEvent.change(await screen.findByLabelText('Project name'), { target: { value: 'Studio' } });
    fireEvent.change(screen.getByLabelText('Describe your business in one prompt'),
      { target: { value: 'A studio' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate from prompt' }));
    await waitFor(() => expect(mocks.generateProjectDraft).toHaveBeenCalledWith(
      id, 'A studio', 'en', 'saved-general', metadata.updated_at));
  });

  it('fails closed on unavailable settings until an explicit retry', async () => {
    mocks.getPreferences.mockRejectedValueOnce(new ApiError(503));
    render(<App />);
    expect(await screen.findByText(/Settings are unavailable or damaged/)).toBeInTheDocument();
    expect(mocks.listProjects).not.toHaveBeenCalled();
    expect(screen.queryByRole('button', { name: 'Settings' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(await screen.findByRole('button', { name: 'English' })).toBeInTheDocument();
    expect(mocks.getPreferences).toHaveBeenCalledTimes(2);
  });

  it('holds first-use onboarding on 409 until an explicit confirmed reload', async () => {
    mocks.savePreferences.mockRejectedValueOnce(new ApiError(409));
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: 'English' }));
    expect(await screen.findByRole('button', { name: 'Reload settings' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'English' })).toBeDisabled();
    expect(mocks.savePreferences).toHaveBeenCalledTimes(1);
    const confirm = vi.fn().mockReturnValueOnce(false).mockReturnValue(true);
    vi.stubGlobal('confirm', confirm);
    fireEvent.click(screen.getByRole('button', { name: 'Reload settings' }));
    expect(mocks.getPreferences).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: 'Reload settings' }));
    expect(await screen.findByRole('button', { name: 'English' })).toBeEnabled();
    expect(mocks.getPreferences).toHaveBeenCalledTimes(2);
  });

  it('retains an unsaved Settings draft after failure and applies only a confirmed save', async () => {
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Settings' }));
    const model = await screen.findByLabelText('OpenAI model');
    fireEvent.change(model, { target: { value: 'draft-general' } });
    mocks.savePreferences.mockRejectedValueOnce(new ApiError(503));
    fireEvent.click(screen.getByRole('button', { name: 'Save settings' }));
    expect(await screen.findByText(/Settings were not saved/)).toBeInTheDocument();
    expect(model).toHaveValue('draft-general');
    expect(mocks.savePreferences).toHaveBeenCalledTimes(3);
    fireEvent.click(screen.getByRole('button', { name: 'Save settings' }));
    await waitFor(() => expect(screen.getByText('Saved')).toBeInTheDocument());
    expect(mocks.savePreferences).toHaveBeenCalledTimes(4);
    expect(mocks.savePreferences.mock.calls[3]?.[0]).toMatchObject({ general_model: 'draft-general' });
  });

  it('does not retry 409 or discard draft before an explicit confirmed reload', async () => {
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Settings' }));
    const model = await screen.findByLabelText('OpenAI model');
    fireEvent.change(model, { target: { value: 'draft-general' } });
    mocks.savePreferences.mockRejectedValueOnce(new ApiError(409));
    fireEvent.click(screen.getByRole('button', { name: 'Save settings' }));
    expect(await screen.findByText(/Settings changed/)).toBeInTheDocument();
    expect(model).toHaveValue('draft-general');
    expect(screen.getByRole('button', { name: 'Save settings' })).toBeDisabled();
    expect(mocks.savePreferences).toHaveBeenCalledTimes(3);
    const confirm = vi.fn().mockReturnValueOnce(false).mockReturnValue(true);
    vi.stubGlobal('confirm', confirm);
    mocks.getPreferences.mockRejectedValueOnce(new ApiError(503));
    mocks.getPreferences.mockResolvedValueOnce({ preferences: {
      schema_version: 1, language: 'en', general_model: 'remote-general', image_model: 'gpt-image-2',
      onboarding_completed: true,
    }, revision: 'c'.repeat(64), projects_directory: 'C:\\Projects' });
    fireEvent.click(screen.getByRole('button', { name: 'Reload settings' }));
    expect(model).toHaveValue('draft-general');
    expect(mocks.getPreferences).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: 'Reload settings' }));
    await waitFor(() => expect(mocks.getPreferences).toHaveBeenCalledTimes(2));
    expect(screen.getByRole('button', { name: 'Save settings' })).toBeDisabled();
    expect(model).toHaveValue('draft-general');
    fireEvent.click(screen.getByRole('button', { name: 'Reload settings' }));
    await waitFor(() => expect(model).toHaveValue('remote-general'));
    expect(mocks.getPreferences).toHaveBeenCalledTimes(3);
    expect(mocks.savePreferences).toHaveBeenCalledTimes(3);
  });
});

describe('publication controls', () => {
  it('keeps ZIP download and revokes its object URL', async () => {
    const create = vi.fn(() => 'blob:local');
    const revoke = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: create, revokeObjectURL: revoke });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    mocks.exportZip.mockResolvedValue(new Blob(['zip'], { type: 'application/zip' }));
    render(<ExportDeploy language="en" projectId={id} ready={async () => metadata.updated_at} onError={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Download site ZIP' }));
    await waitFor(() => expect(mocks.exportZip).toHaveBeenCalledWith(id, metadata.updated_at));
    await waitFor(() => expect(revoke).toHaveBeenCalledWith('blob:local'));
    expect(screen.getByRole('button', { name: 'Export site folder' })).toBeInTheDocument();
    expect(mocks.exportFolder).not.toHaveBeenCalled();
    vi.restoreAllMocks();
  });

  it('requires folder confirmation and a saved timestamp, then displays and copies the returned path', async () => {
    const confirm = vi.fn(() => false);
    const copy = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('confirm', confirm);
    vi.stubGlobal('navigator', { clipboard: { writeText: copy } });
    const path = 'C:\\Users\\Tester\\Documents\\AURORA\\Projects\\studio\\exports\\aurora-site-123';
    mocks.exportFolder.mockResolvedValue(path);
    const ready = vi.fn().mockResolvedValueOnce(null).mockResolvedValueOnce(metadata.updated_at);
    render(<ExportDeploy language="en" projectId={id} ready={ready} onError={vi.fn()} />);
    expect(mocks.exportFolder).not.toHaveBeenCalled();
    const button = screen.getByRole('button', { name: 'Export site folder' });
    fireEvent.click(button);
    expect(ready).not.toHaveBeenCalled();
    expect(mocks.exportFolder).not.toHaveBeenCalled();
    confirm.mockReturnValue(true);
    fireEvent.click(button);
    await waitFor(() => expect(ready).toHaveBeenCalledTimes(1));
    expect(mocks.exportFolder).not.toHaveBeenCalled();
    fireEvent.click(button);
    await waitFor(() => expect(mocks.exportFolder).toHaveBeenCalledWith(id, metadata.updated_at));
    expect(mocks.exportFolder).toHaveBeenCalledTimes(1);
    expect(ready.mock.invocationCallOrder[1]).toBeLessThan(mocks.exportFolder.mock.invocationCallOrder[0] ?? 0);
    expect(screen.getByLabelText('Finished-site folder')).toHaveValue(path);
    expect(screen.queryByRole('link', { name: path })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Copy path' }));
    await waitFor(() => expect(copy).toHaveBeenCalledWith(path));
  });

  it('keeps the path selectable when clipboard access fails', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true));
    vi.stubGlobal('navigator', { clipboard: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } });
    mocks.exportFolder.mockResolvedValue('C:\\Projects\\exports\\aurora-site-123');
    render(<ExportDeploy language="en" projectId={id} ready={async () => metadata.updated_at} onError={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Export site folder' }));
    await screen.findByDisplayValue('C:\\Projects\\exports\\aurora-site-123');
    fireEvent.click(screen.getByRole('button', { name: 'Copy path' }));
    expect(await screen.findByText(/Select it and copy it manually/)).toBeInTheDocument();
    expect(screen.getByLabelText('Finished-site folder')).toHaveAttribute('readonly');
  });

  it('gates publication while pending and never retries or reports uncertain export as successful', async () => {
    let fail: ((error: unknown) => void) | undefined;
    mocks.exportFolder.mockImplementation(() => new Promise<string>((_resolve, reject) => { fail = reject; }));
    const onError = vi.fn();
    vi.stubGlobal('confirm', vi.fn(() => true));
    render(<ExportDeploy language="en" projectId={id} ready={async () => metadata.updated_at} onError={onError} />);
    fireEvent.click(screen.getByRole('button', { name: 'Export site folder' }));
    await waitFor(() => expect(mocks.exportFolder).toHaveBeenCalledTimes(1));
    expect(screen.getByRole('button', { name: 'Export site folder' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Download site ZIP' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Deploy to Netlify' })).toBeDisabled();
    fail?.(new ApiError(409));
    expect(await screen.findByText(/Inspect the project’s exports/)).toBeInTheDocument();
    expect(onError).toHaveBeenCalledWith(expect.objectContaining({ status: 409 }));
    expect(screen.queryByLabelText('Finished-site folder')).not.toBeInTheDocument();
    expect(mocks.exportFolder).toHaveBeenCalledTimes(1);
  });

  it.each([new TypeError('network'), new Error('Invalid folder export response')])(
    'does not auto-retry an uncertain folder response (%s)', async (failure) => {
      vi.stubGlobal('confirm', vi.fn(() => true));
      mocks.exportFolder.mockRejectedValue(failure);
      const onError = vi.fn();
      render(<ExportDeploy language="en" projectId={id} ready={async () => metadata.updated_at} onError={onError} />);
      fireEvent.click(screen.getByRole('button', { name: 'Export site folder' }));
      expect(await screen.findByText(/Inspect the project’s exports/)).toBeInTheDocument();
      expect(onError).toHaveBeenCalledWith(failure);
      expect(screen.queryByLabelText('Finished-site folder')).not.toBeInTheDocument();
      expect(mocks.exportFolder).toHaveBeenCalledTimes(1);
    },
  );

  it('shows the fixed local destination in Russian without sending a request on render', () => {
    render(<ExportDeploy language="ru" projectId={id} ready={async () => metadata.updated_at} onError={vi.fn()} />);
    expect(screen.getByRole('button', { name: 'Экспортировать папку сайта' })).toBeInTheDocument();
    expect(screen.getByText(/новую папку в exports\//)).toBeInTheDocument();
    expect(mocks.exportFolder).not.toHaveBeenCalled();
  });

  it('requires explicit deploy confirmation and displays only recovery IDs on failure', async () => {
    const confirm = vi.fn(() => false);
    vi.stubGlobal('confirm', confirm);
    mocks.deployNetlify.mockRejectedValue(new ApiError(503, { site_id: id, deploy_id: null }));
    render(<ExportDeploy language="en" projectId={id} ready={async () => metadata.updated_at} onError={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Deploy to Netlify' }));
    expect(mocks.deployNetlify).not.toHaveBeenCalled();
    confirm.mockReturnValue(true);
    fireEvent.click(screen.getByRole('button', { name: 'Deploy to Netlify' }));
    await waitFor(() => expect(mocks.deployNetlify).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole('alert')).toHaveTextContent(id);
    expect(screen.getByRole('alert')).toHaveTextContent('Inspect Netlify');
  });
});
