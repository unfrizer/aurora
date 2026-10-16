import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { useState } from 'react';
import { blankEditor } from '../src/editor';
import { GuidedImageCompletion } from '../src/components/GuidedImageCompletion';
import type { EditorDocument, Language, ProjectDocument } from '../src/types';

const projectId = '00000000-0000-4000-8000-000000000001';
const assetPath = `assets/${'a'.repeat(64)}.png`;
const source = '2026-10-16T00:00:00Z';
const uuid = (number: number) => `00000000-0000-4000-8000-${number.toString().padStart(12, '0')}`;

function document(editor: EditorDocument, updatedAt = source): ProjectDocument {
  return { metadata: { project_id: projectId, name: 'Studio', format_version: '1',
    created_at: source, updated_at: updatedAt }, state: { editor, opaque: { preserved: true } } };
}

function harness(initial: EditorDocument, language: Language = 'en') {
  const onLock = vi.fn();
  const onError = vi.fn();
  const onExit = vi.fn();
  let saved = document(initial);
  function AppHarness() {
    const [current, setCurrent] = useState(saved);
    const editor = current.state.editor as EditorDocument;
    return <GuidedImageCompletion language={language} projectId={projectId} editor={editor} model="gpt-image-2"
      onSnapshot={async () => ({ editor, updatedAt: current.metadata.updated_at })}
      onDocument={(next) => { saved = next; setCurrent(next); }}
      onLock={onLock} onError={onError} onExit={onExit} />;
  }
  render(<AppHarness />);
  return { onLock, onError, onExit, saved: () => saved };
}

function fakeFetch() {
  let saved: ProjectDocument | null = null;
  let saveCount = 0;
  const fetcher = vi.fn(async (url: string, init?: RequestInit) => {
    const body = init?.body ? JSON.parse(init.body as string) as Record<string, unknown> : {};
    if (url.endsWith('/generation/image') && init?.method === 'POST') {
      return new Response(JSON.stringify({ job_id: projectId, status: 'completed',
        source_updated_at: body.expected_updated_at, asset_path: assetPath, failure: null }), { status: 200 });
    }
    if (url.endsWith('/editor') && init?.method === 'PUT') {
      saveCount += 1;
      saved = document(body.editor as EditorDocument, `2026-10-16T00:00:0${saveCount}Z`);
      return new Response(JSON.stringify(saved), { status: 200 });
    }
    if (url.endsWith(`/projects/${projectId}`) && init?.method === 'GET' && saved) {
      return new Response(JSON.stringify(saved), { status: 200 });
    }
    throw new Error(`Unexpected local request: ${url}`);
  });
  vi.stubGlobal('fetch', fetcher);
  return fetcher;
}

beforeEach(() => vi.stubGlobal('confirm', vi.fn(() => true)));
afterEach(() => vi.unstubAllGlobals());

describe('guided one-prompt image completion', () => {
  it('offers an optional bounded ID-frozen plan in English and Russian without a paid call', () => {
    const base = blankEditor('Studio', 'en');
    const pages = Array.from({ length: 6 }, (_, index) => ({
      ...base.pages[0]!, id: uuid(index + 10), title: `Page ${index + 1}`, heading: `Heading ${index + 1}`,
      sections: [
        { ...base.pages[0]!.sections[0]!, id: uuid(index * 2 + 100), heading: `Used ${index + 1}`,
          image_path: index === 0 ? assetPath : null },
        { ...base.pages[0]!.sections[0]!, id: uuid(index * 2 + 101), heading: `Empty ${index + 1}` },
      ],
    }));
    harness({ ...base, brand: { ...base.brand, tagline: 'Clear work' }, pages });
    expect(screen.getByRole('heading', { name: 'Complete project images' })).toBeInTheDocument();
    expect(screen.getByText(/Possible initial paid requests: 5/)).toBeInTheDocument();
    expect(screen.getByText(/Explicit retries may add charges/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Open workspace' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    expect(screen.getByText('Create a brand logo for "Studio". Tagline: "Clear work". Language: en.')).toBeInTheDocument();
    for (let index = 1; index <= 4; index += 1) expect(screen.getByText(`Page ${index} / ${index === 1 ? 'Empty' : 'Used'} ${index}`)).toBeInTheDocument();
    expect(screen.queryByText('Page 5 / Used 5')).not.toBeInTheDocument();
    expect(screen.queryByText('Page 6 / Used 6')).not.toBeInTheDocument();

  });

  it('uses visible suggestions, separate charge consent, strict P6 result and explicit save per target', async () => {
    const editor = blankEditor('Studio', 'en');
    editor.brand.tagline = 'Quiet design';
    editor.pages[0]!.sections[0]!.body = 'Private section body must not enter an image prompt';
    const fetcher = fakeFetch();
    const consent = vi.fn(() => true);
    vi.stubGlobal('confirm', consent);
    const { saved } = harness(editor);
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    fireEvent.click(screen.getByRole('button', { name: 'Review and generate image' }));
    const logo = screen.getByRole('dialog', { name: 'Generate image' });
    const suggested = 'Create a brand logo for "Studio". Tagline: "Quiet design". Language: en.';
    expect(within(logo).getByLabelText('Describe the image')).toHaveValue(suggested);
    expect(fetcher).not.toHaveBeenCalled();
    fireEvent.click(within(logo).getByRole('button', { name: 'Generate image' }));
    expect(consent).toHaveBeenCalledWith(expect.stringContaining('displayed description to OpenAI'));
    await within(logo).findByText('Stored in project, not attached');
    expect(fetcher).toHaveBeenCalledTimes(1);
    const [imageUrl, imageInit] = fetcher.mock.calls[0]!;
    expect(imageUrl).toBe(`/api/v1/projects/${projectId}/generation/image`);
    expect(imageInit?.headers).toEqual({ 'X-Aurora-Request': '1', 'Content-Type': 'application/json' });
    expect(JSON.parse(imageInit!.body as string)).toEqual({ prompt: suggested, model: 'gpt-image-2',
      expected_updated_at: source, confirm_generation: true });
    expect(saved().state.editor).toEqual(editor);
    fireEvent.click(within(logo).getByRole('button', { name: 'Attach and save' }));
    await waitFor(() => expect(saved().state.editor).toMatchObject({ brand: { logo_path: assetPath } }));
    expect(fetcher).toHaveBeenCalledTimes(2);
    expect(screen.getAllByText('Studio / About').length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole('button', { name: 'Review and generate image' }));
    const section = screen.getByRole('dialog', { name: 'Generate image' });
    expect(within(section).getByLabelText('Describe the image')).toHaveValue(
      'Create an image for page "Studio", section "About", brand "Studio". Language: en.');
    expect(within(section).getByRole('button', { name: 'Generate image' })).toBeDisabled();
    fireEvent.change(within(section).getByLabelText('Enter image description for the section.'),
      { target: { value: 'A quiet studio' } });
    fireEvent.click(within(section).getByRole('button', { name: 'Generate image' }));
    await within(section).findByText('Stored in project, not attached');
    const sectionBody = JSON.parse(fetcher.mock.calls[2]![1]!.body as string) as Record<string, unknown>;
    expect(sectionBody.prompt).toBe('Create an image for page "Studio", section "About", brand "Studio". Language: en.');
    expect(JSON.stringify(sectionBody)).not.toContain('Private section body');
    fireEvent.click(within(section).getByRole('button', { name: 'Attach and save' }));
    await waitFor(() => expect((saved().state.editor as EditorDocument).pages[0]?.sections[0])
      .toMatchObject({ image_path: assetPath, image_alt: 'A quiet studio' }));
    expect(fetcher).toHaveBeenCalledTimes(4);
    expect(screen.getByText(/All slots in this plan are filled/)).toBeInTheDocument();
  });

  it('allows skipping and leaving without a paid call; Russian labels are available', () => {
    const editor = blankEditor('Студия', 'ru');
    const fetcher = fakeFetch();
    const { onExit } = harness(editor, 'ru');
    expect(screen.getByRole('button', { name: 'Перейти в редактор' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Посмотреть план изображений' }));
    fireEvent.click(screen.getByRole('button', { name: 'Пропустить это изображение' }));
    expect(screen.getAllByText('Студия / О нас').length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole('button', { name: 'Пропустить это изображение' }));
    expect(screen.getByText(/План завершён частично/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Перейти в редактор' }));
    expect(onExit).toHaveBeenCalledTimes(1);
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('refuses oversized visible suggestions without truncation and leaves the slot untouched', () => {
    const editor = blankEditor('Studio', 'en');
    editor.brand.name = 'x'.repeat(8200);
    const fetcher = fakeFetch();
    harness(editor);
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    fireEvent.click(screen.getByRole('button', { name: 'Review and generate image' }));
    const dialog = screen.getByRole('dialog', { name: 'Generate image' });
    expect((within(dialog).getByLabelText('Describe the image') as HTMLTextAreaElement).value).toContain('x'.repeat(8200));
    expect(within(dialog).getByRole('button', { name: 'Generate image' })).toBeDisabled();
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('does not send a paid call when guided consent is declined', () => {
    const fetcher = fakeFetch();
    vi.stubGlobal('confirm', vi.fn(() => false));
    harness(blankEditor('Studio', 'en'));
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    fireEvent.click(screen.getByRole('button', { name: 'Review and generate image' }));
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    expect(fetcher).not.toHaveBeenCalled();
    expect(screen.getByRole('dialog', { name: 'Generate image' })).toBeInTheDocument();
  });

  it('rejects a malformed P6 result without attaching or retrying', async () => {
    const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify({ job_id: projectId,
      status: 'completed', source_updated_at: source, asset_path: assetPath, failure: null,
      extra: 'unapproved',
    }), { status: 200 }));
    vi.stubGlobal('fetch', fetcher);
    const { saved, onError } = harness(blankEditor('Studio', 'en'));
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    fireEvent.click(screen.getByRole('button', { name: 'Review and generate image' }));
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    expect(await screen.findByText(/outcome is unknown/)).toBeInTheDocument();
    expect(onError).toHaveBeenCalledTimes(1);
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect((saved().state.editor as EditorDocument).brand.logo_path).toBeNull();
  });

  it('keeps a discarded stored asset unattached and returns to an idle, skippable target', async () => {
    const fetcher = fakeFetch();
    const { saved, onLock } = harness(blankEditor('Studio', 'en'));
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    fireEvent.click(screen.getByRole('button', { name: 'Review and generate image' }));
    const dialog = screen.getByRole('dialog', { name: 'Generate image' });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Generate image' }));
    await within(dialog).findByText('Stored in project, not attached');
    const unload = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(unload);
    expect(unload.defaultPrevented).toBe(true);
    fireEvent.click(within(dialog).getByRole('button', { name: 'Discard image' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Skip this image' })).toBeInTheDocument();
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher.mock.calls.some(([, init]) => init?.method === 'DELETE')).toBe(false);
    expect((saved().state.editor as EditorDocument).brand.logo_path).toBeNull();
    expect(onLock).toHaveBeenNthCalledWith(1, true);
    expect(onLock).toHaveBeenLastCalledWith(false);
  });

  it('shows safe terminal failure and uncertain transport without automatic retries or attachment', async () => {
    const editor = blankEditor('Studio', 'en');
    const fetcher = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ job_id: projectId,
      status: 'failed', source_updated_at: source, asset_path: null,
      failure: { category: 'rate_limited', message: 'Safe failure', retryable: true } }), { status: 200 }))
      .mockRejectedValueOnce(new TypeError('private network detail'));
    vi.stubGlobal('fetch', fetcher);
    const { saved, onError } = harness(editor);
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    fireEvent.click(screen.getByRole('button', { name: 'Review and generate image' }));
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Safe failure');
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(saved().state.editor).toEqual(editor);
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(fetcher).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    expect(await screen.findByText(/outcome is unknown/)).toBeInTheDocument();
    expect(onError).toHaveBeenCalledTimes(1);
    expect(screen.queryByText('private network detail')).not.toBeInTheDocument();
    expect(fetcher).toHaveBeenCalledTimes(2);
    expect(saved().state.editor).toEqual(editor);
  });

  it('reconciles only frozen empty targets after a 409 reload without another paid call', async () => {
    const editor = blankEditor('Studio', 'en');
    const revised = { ...editor, brand: { ...editor.brand, logo_path: assetPath } };
    const newer = '2026-10-16T00:01:00Z';
    let puts = 0;
    const fetcher = vi.fn(async (url: string, init?: RequestInit) => {
      const body = init?.body ? JSON.parse(init.body as string) as Record<string, unknown> : {};
      if (url.endsWith('/generation/image') && init?.method === 'POST') return new Response(JSON.stringify({
        job_id: projectId, status: 'completed', source_updated_at: body.expected_updated_at,
        asset_path: assetPath, failure: null,
      }), { status: 200 });
      if (url.endsWith('/editor') && init?.method === 'PUT') {
        puts += 1;
        return puts === 1 ? new Response(JSON.stringify({ error: { code: 409 } }), { status: 409 }) :
          new Response(JSON.stringify(document(body.editor as EditorDocument, '2026-10-16T00:02:00Z')), { status: 200 });
      }
      if (url.endsWith(`/projects/${projectId}`) && init?.method === 'GET') {
        return new Response(JSON.stringify(document(revised, newer)), { status: 200 });
      }
      throw new Error(`Unexpected local request: ${url}`);
    });
    vi.stubGlobal('fetch', fetcher);
    const { saved } = harness(editor);
    fireEvent.click(screen.getByRole('button', { name: 'Review image plan' }));
    fireEvent.click(screen.getByRole('button', { name: 'Review and generate image' }));
    fireEvent.click(screen.getByRole('button', { name: 'Generate image' }));
    await screen.findByText('Stored in project, not attached');
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    await screen.findByText(/The project changed/);
    fireEvent.click(screen.getByRole('button', { name: 'Reload project and choose target' }));
    const select = await screen.findByLabelText('Attach to');
    expect(screen.queryByRole('option', { name: 'Brand logo' })).not.toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Studio / About' })).toBeInTheDocument();
    const page = editor.pages[0]!;
    const section = page.sections[0]!;
    fireEvent.change(select, { target: { value: `${page.id}/${section.id}` } });
    fireEvent.change(screen.getByLabelText('Enter image description for the section.'),
      { target: { value: 'A studio section' } });
    fireEvent.click(screen.getByRole('button', { name: 'Attach and save' }));
    await waitFor(() => expect((saved().state.editor as EditorDocument).pages[0]?.sections[0])
      .toMatchObject({ image_path: assetPath, image_alt: 'A studio section' }));
    expect(puts).toBe(2);
    expect(fetcher.mock.calls.filter(([url, init]) => url.endsWith('/generation/image') && init?.method === 'POST')).toHaveLength(1);
    expect(screen.getByText(/All slots in this plan are filled/)).toBeInTheDocument();
  });
});
