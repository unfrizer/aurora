import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { EditorDocument, ProjectDocument } from '../src/types';
import { validImageInputs } from '../src/types';
import { blankEditor } from '../src/editor';

const mocks = vi.hoisted(() => ({ generateImage: vi.fn(), saveEditor: vi.fn(), openProject: vi.fn(), deleteRaster: vi.fn() }));
vi.mock('../src/api', async (original) => ({ ...(await original<typeof import('../src/api')>()), ...mocks }));

import { ApiError } from '../src/api';
import { ImageGeneration, type ImageSnapshot } from '../src/components/ImageGeneration';

const projectId = '00000000-0000-4000-8000-000000000001';
const path = `assets/${'a'.repeat(64)}.png`;
const initial = blankEditor('Studio', 'en');
const timestamp = '2026-10-16T00:00:00Z';
const metadata = { project_id: projectId, name: 'Studio', format_version: '1', created_at: timestamp, updated_at: timestamp };
const result = { job_id: projectId, status: 'completed' as const, source_updated_at: timestamp, asset_path: path, failure: null };

function document(editor: EditorDocument, updatedAt = timestamp): ProjectDocument {
  return { metadata: { ...metadata, updated_at: updatedAt }, state: { editor, opaque: { preserved: true } } };
}

function harness(target: { kind: 'logo' } | { kind: 'section'; pageId: string; sectionId: string } = { kind: 'logo' },
  language: 'en' | 'ru' = 'en', model = 'gpt-image-2') {
  const snapshot: ImageSnapshot = { editor: initial, updatedAt: timestamp };
  const onSnapshot = vi.fn().mockResolvedValue(snapshot);
  const onDocument = vi.fn();
  const onError = vi.fn();
  const onClose = vi.fn();
  render(<ImageGeneration language={language} projectId={projectId} target={target} targetLabel="Studio target"
    model={model} onSnapshot={onSnapshot} onDocument={onDocument} onError={onError} onClose={onClose} />);
  return { onSnapshot, onDocument, onError, onClose };
}

beforeEach(() => {
  vi.clearAllMocks();
  mocks.generateImage.mockResolvedValue(result);
  mocks.saveEditor.mockImplementation(async (_id: string, editor: EditorDocument) => document(editor));
  mocks.openProject.mockResolvedValue(document(initial));
  vi.stubGlobal('confirm', vi.fn(() => true));
});

afterEach(() => vi.unstubAllGlobals());

describe('reviewed image generation', () => {
  it('requires bounded unchanged prompt, consent and a clean saved snapshot before one paid attempt', async () => {
    const confirm = vi.fn(() => false);
    vi.stubGlobal('confirm', confirm);
    const { onSnapshot } = harness();
    const button = screen.getByRole('button', { name: 'Generate image' });
    expect(button).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Describe the image'), { target: { value: '  forest scene  ' } });
    fireEvent.click(button);
    expect(confirm).toHaveBeenCalledWith(expect.stringContaining('may incur a charge'));
    expect(onSnapshot).not.toHaveBeenCalled();
    expect(mocks.generateImage).not.toHaveBeenCalled();
    confirm.mockReturnValue(true);
    fireEvent.click(button);
    await screen.findByText('Stored in project, not attached');
    expect(onSnapshot).toHaveBeenCalledTimes(1);
    expect(mocks.generateImage).toHaveBeenCalledExactlyOnceWith(projectId, '  forest scene  ', 'gpt-image-2', timestamp);
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(validImageInputs('x'.repeat(8192), 'm')).toBe(true);
    expect(validImageInputs('x'.repeat(8193), 'm')).toBe(false);
    expect(validImageInputs('\ud800', 'm')).toBe(false);
  });

  it('shows stored candidate and attaches only after a second explicit action', async () => {
    const { onDocument, onClose } = harness();
    fireEvent.change(screen.getByLabelText('Describe the image'), { target: { value: 'A logo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    expect(await screen.findByText('Stored in project, not attached')).toBeInTheDocument();
    expect(screen.getByRole('img')).toHaveAttribute('src', `/api/v1/projects/${projectId}/assets/${'a'.repeat(64)}.png`);
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    const [id, next, expected] = mocks.saveEditor.mock.calls[0] as [string, EditorDocument, string];
    expect(id).toBe(projectId);
    expect(expected).toBe(timestamp);
    expect(next.brand.logo_path).toBe(path);
    expect(next.pages).toEqual(initial.pages);
    await waitFor(() => expect(onDocument).toHaveBeenCalledTimes(1));
    expect(onClose).toHaveBeenCalledTimes(1);
    expect(mocks.deleteRaster).not.toHaveBeenCalled();
  });

  it('requires user-authored section alt text and preserves all other editor fields', async () => {
    const section = initial.pages[0]?.sections[0];
    const page = initial.pages[0];
    expect(section && page).toBeTruthy();
    harness({ kind: 'section', pageId: page!.id, sectionId: section!.id }, 'ru');
    fireEvent.change(screen.getByLabelText('Опишите нужное изображение'), { target: { value: 'Лес' } });
    expect(screen.getByRole('button', { name: 'Сгенерировать изображение' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Введите описание изображения для секции.'), { target: { value: 'Зелёный лес' } });
    fireEvent.click(screen.getByRole('button', { name: 'Сгенерировать изображение' }));
    await screen.findByText('Сохранено в проекте, но не прикреплено');
    fireEvent.click(screen.getByRole('button', { name: 'Прикрепить и сохранить' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(1));
    const next = mocks.saveEditor.mock.calls[0]?.[1] as EditorDocument;
    expect(next.pages[0]?.sections[0]).toEqual({ ...section, image_path: path, image_alt: 'Зелёный лес' });
    expect(next.brand).toEqual(initial.brand);
  });

  it('does not delete the stored asset when discarded and warns on unload while reviewing', async () => {
    const { onClose } = harness();
    fireEvent.change(screen.getByLabelText('Describe the image'), { target: { value: 'A logo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    await screen.findByText('Stored in project, not attached');
    await waitFor(() => {
      const unload = new Event('beforeunload', { cancelable: true });
      window.dispatchEvent(unload);
      expect(unload.defaultPrevented).toBe(true);
    });
    fireEvent.click(screen.getByRole('button', { name: 'Discard image' }));
    expect(onClose).toHaveBeenCalledTimes(1);
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    expect(mocks.deleteRaster).not.toHaveBeenCalled();
  });

  it('retains the candidate after 409 and requires reload, target selection and fresh explicit attachment', async () => {
    const revised = { ...initial, brand: { ...initial.brand, tagline: 'Changed elsewhere' } };
    const newer = '2026-10-16T01:00:00Z';
    mocks.saveEditor.mockRejectedValueOnce(new ApiError(409))
      .mockImplementationOnce(async (_id: string, editor: EditorDocument) => document(editor, '2026-10-16T02:00:00Z'));
    mocks.openProject.mockResolvedValue(document(revised, newer));
    const { onSnapshot, onDocument } = harness();
    fireEvent.change(screen.getByLabelText('Describe the image'), { target: { value: 'A logo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    await screen.findByText('Stored in project, not attached');
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    expect(await screen.findByText(/The project changed/)).toBeInTheDocument();
    expect(mocks.saveEditor).toHaveBeenCalledTimes(1);
    expect(mocks.saveEditor.mock.calls[0]?.[2]).toBe(timestamp);
    onSnapshot.mockResolvedValue({ editor: revised, updatedAt: newer });
    fireEvent.click(screen.getByRole('button', { name: 'Reload project and choose target' }));
    await screen.findByLabelText('Attach to');
    expect(screen.getByRole('button', { name: 'Attach and save' })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Attach to'), { target: { value: 'logo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(2));
    expect(mocks.saveEditor.mock.calls[1]?.[2]).toBe(newer);
    expect((mocks.saveEditor.mock.calls[1]?.[1] as EditorDocument).brand.tagline).toBe('Changed elsewhere');
    expect(mocks.generateImage).toHaveBeenCalledTimes(1);
    expect(onDocument).toHaveBeenCalledTimes(2);
  });

  it('never auto-retries terminal failure, network uncertainty or malformed saved editor', async () => {
    mocks.generateImage.mockResolvedValueOnce({ job_id: projectId, status: 'failed', source_updated_at: timestamp,
      asset_path: null, failure: { category: 'rate_limited', message: 'Safe message', retryable: true } });
    const { onError } = harness();
    fireEvent.change(screen.getByLabelText('Describe the image'), { target: { value: 'A logo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Safe message');
    expect(mocks.generateImage).toHaveBeenCalledTimes(1);
    expect(mocks.saveEditor).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    mocks.generateImage.mockRejectedValueOnce(new TypeError('private provider detail'));
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    expect(await screen.findByText(/outcome is unknown/)).toBeInTheDocument();
    expect(onError).toHaveBeenCalled();
    expect(mocks.generateImage).toHaveBeenCalledTimes(2);
    expect(screen.queryByText('private provider detail')).not.toBeInTheDocument();
  });

  it('does not call OpenAI if the saved editor is unavailable or the selected target disappeared', async () => {
    const page = initial.pages[0]!;
    const section = page.sections[0]!;
    const { onSnapshot, onError } = harness({ kind: 'section', pageId: page.id, sectionId: section.id });
    fireEvent.change(screen.getByLabelText('Describe the image'), { target: { value: 'A scene' } });
    fireEvent.change(screen.getByLabelText('Enter image description for the section.'), { target: { value: 'A scene' } });
    onSnapshot.mockResolvedValueOnce(null);
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    await waitFor(() => expect(onSnapshot).toHaveBeenCalledTimes(1));
    expect(mocks.generateImage).not.toHaveBeenCalled();
    onSnapshot.mockResolvedValueOnce({ editor: { ...initial, pages: [{ ...page, sections: [] }] }, updatedAt: timestamp });
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(1));
    expect(mocks.generateImage).not.toHaveBeenCalled();
  });

  it('retains the stored candidate when save response is malformed or reload has unsupported editor', async () => {
    mocks.saveEditor.mockResolvedValueOnce({ metadata, state: { editor: { schema_version: 2 } } });
    const { onError, onDocument } = harness();
    fireEvent.change(screen.getByLabelText('Describe the image'), { target: { value: 'A logo' } });
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    await screen.findByText('Stored in project, not attached');
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(1));
    expect(screen.getByText('Stored in project, not attached')).toBeInTheDocument();
    expect(onDocument).not.toHaveBeenCalled();
    mocks.saveEditor.mockRejectedValueOnce(new ApiError(409));
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    await screen.findByText(/The project changed/);
    mocks.openProject.mockResolvedValueOnce({ metadata, state: { editor: { schema_version: 2 } } });
    fireEvent.click(screen.getByRole('button', { name: 'Reload project and choose target' }));
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(2));
    expect(screen.getByText('Stored in project, not attached')).toBeInTheDocument();
    expect(screen.queryByLabelText('Attach to')).not.toBeInTheDocument();
    expect(mocks.generateImage).toHaveBeenCalledTimes(1);
  });

  it('blocks a guided paid request when its frozen target was filled before the call', async () => {
    const onSnapshot = vi.fn().mockResolvedValue({ editor: { ...initial, brand: { ...initial.brand, logo_path: path } }, updatedAt: timestamp });
    const onError = vi.fn();
    render(<ImageGeneration language="en" projectId={projectId} target={{ kind: 'logo' }} targetLabel="Brand logo"
      model="gpt-image-2" initialPrompt="Visible proposed logo" allowedTargets={[{ kind: 'logo' }]}
      requireEmptyTarget guided onSnapshot={onSnapshot} onDocument={vi.fn()} onError={onError} onClose={vi.fn()} />);
    expect(screen.getByLabelText('Describe the image')).toHaveValue('Visible proposed logo');
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    await waitFor(() => expect(onError).toHaveBeenCalledTimes(1));
    expect(mocks.generateImage).not.toHaveBeenCalled();
    expect(mocks.saveEditor).not.toHaveBeenCalled();
  });

  it('reselects only a frozen empty guided target after 409 and never repeats the paid call', async () => {
    const page = initial.pages[0]!;
    const section = page.sections[0]!;
    const newer = '2026-10-16T01:00:00Z';
    const revised = { ...initial, brand: { ...initial.brand, logo_path: path } };
    mocks.saveEditor.mockRejectedValueOnce(new ApiError(409))
      .mockImplementationOnce(async (_id: string, editor: EditorDocument) => document(editor, '2026-10-16T02:00:00Z'));
    mocks.openProject.mockResolvedValue(document(revised, newer));
    const onSnapshot = vi.fn().mockResolvedValueOnce({ editor: initial, updatedAt: timestamp })
      .mockResolvedValueOnce({ editor: initial, updatedAt: timestamp })
      .mockResolvedValue({ editor: revised, updatedAt: newer });
    const onAttached = vi.fn();
    render(<ImageGeneration language="en" projectId={projectId} target={{ kind: 'logo' }} targetLabel="Brand logo"
      model="gpt-image-2" initialPrompt="Visible proposed logo" allowedTargets={[
        { kind: 'logo' }, { kind: 'section', pageId: page.id, sectionId: section.id },
      ]} requireEmptyTarget guided onSnapshot={onSnapshot} onDocument={vi.fn()}
      onError={vi.fn()} onClose={vi.fn()} onAttached={onAttached} />);
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    await screen.findByText('Stored in project, not attached');
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    await screen.findByText(/The project changed/);
    fireEvent.click(screen.getByRole('button', { name: 'Reload project and choose target' }));
    const chooser = await screen.findByLabelText('Attach to');
    expect(screen.queryByRole('option', { name: 'Brand logo' })).not.toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Studio / About' })).toBeInTheDocument();
    fireEvent.change(chooser, { target: { value: `${page.id}/${section.id}` } });
    fireEvent.change(screen.getByLabelText('Enter image description for the section.'),
      { target: { value: 'A studio section' } });
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    await waitFor(() => expect(mocks.saveEditor).toHaveBeenCalledTimes(2));
    const attached = mocks.saveEditor.mock.calls[1]?.[1] as EditorDocument;
    expect(attached.brand.logo_path).toBe(path);
    expect(attached.pages[0]?.sections[0]).toMatchObject({ image_path: path, image_alt: 'A studio section' });
    expect(mocks.saveEditor.mock.calls[1]?.[2]).toBe(newer);
    expect(mocks.generateImage).toHaveBeenCalledTimes(1);
    expect(onAttached).toHaveBeenCalledWith({ kind: 'section', pageId: page.id, sectionId: section.id });
  });
});
