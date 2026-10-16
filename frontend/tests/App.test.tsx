import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { EditorDocument, ProjectDocument } from '../src/types';
import { blankEditor } from '../src/editor';

const mocks = vi.hoisted(() => ({
  listProjects: vi.fn(), createProject: vi.fn(), openProject: vi.fn(), saveEditor: vi.fn(),
  renameProject: vi.fn(), deleteProject: vi.fn(), credentialStatus: vi.fn(),
  setCredential: vi.fn(), deleteCredential: vi.fn(), exportZip: vi.fn(), deployNetlify: vi.fn(),
  generateText: vi.fn(), uploadRaster: vi.fn(), deleteRaster: vi.fn(),
  generateProjectDraft: vi.fn(),
  generateImage: vi.fn(),
}));

vi.mock('../src/api', async (original) => ({ ...(await original<typeof import('../src/api')>()), ...mocks }));

import App from '../src/App';
import { ApiError } from '../src/api';
import { ExportDeploy } from '../src/components/ExportDeploy';

const id = '00000000-0000-4000-8000-000000000111';
const metadata = { project_id: id, name: 'Studio', format_version: '1', created_at: '2026-10-09T00:00:00Z', updated_at: '2026-10-09T01:00:00Z' };
const empty: ProjectDocument = { metadata, state: {} };

function withEditor(editor: EditorDocument): ProjectDocument {
  return { metadata: { ...metadata, updated_at: '2026-10-09T02:00:00Z' }, state: { editor } };
}

async function enter(language: 'ru' | 'en' = 'en') {
  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: language === 'en' ? 'English' : 'Русский' }));
  fireEvent.click(screen.getByRole('button', { name: language === 'en' ? 'Start' : 'Начать' }));
  await screen.findByRole('heading', { name: language === 'en' ? 'Projects' : 'Проекты' });
}

beforeEach(() => {
  vi.clearAllMocks();
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

afterEach(() => vi.unstubAllGlobals());

describe('workspace flow', () => {
  it('chooses RU/EN, creates an empty project, then explicitly initializes P7', async () => {
    await enter('ru');
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

  it('keeps a separate session image model and locks workspace navigation while an image is pending or unreviewed', async () => {
    let finish: ((result: unknown) => void) | undefined;
    mocks.generateImage.mockImplementation(() => new Promise((resolve) => { finish = resolve; }));
    vi.stubGlobal('confirm', vi.fn(() => true));
    await enter();
    fireEvent.click(screen.getByRole('button', { name: 'Settings' }));
    const model = await screen.findByLabelText('OpenAI image model (this session only)');
    expect(model).toHaveValue('gpt-image-2');
    fireEvent.change(model, { target: { value: 'custom-image-model' } });
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

describe('publication controls', () => {
  it('downloads only ZIP and revokes its object URL', async () => {
    const create = vi.fn(() => 'blob:local');
    const revoke = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: create, revokeObjectURL: revoke });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    mocks.exportZip.mockResolvedValue(new Blob(['zip'], { type: 'application/zip' }));
    render(<ExportDeploy language="en" projectId={id} ready={async () => metadata.updated_at} onError={vi.fn()} />);
    fireEvent.click(screen.getByRole('button', { name: 'Download site ZIP' }));
    await waitFor(() => expect(mocks.exportZip).toHaveBeenCalledWith(id, metadata.updated_at));
    await waitFor(() => expect(revoke).toHaveBeenCalledWith('blob:local'));
    expect(screen.queryByRole('button', { name: /folder/i })).not.toBeInTheDocument();
    vi.restoreAllMocks();
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
