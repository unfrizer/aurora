import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, createProject, credentialStatus, deployNetlify, exportZip, generateText, saveEditor, setCredential, uploadRaster } from '../src/api';
import { blankEditor } from '../src/editor';

const id = '00000000-0000-4000-8000-000000000001';
const metadata = { project_id: id, name: 'Studio', format_version: '1', created_at: 'now', updated_at: 'then' };

afterEach(() => vi.unstubAllGlobals());

describe('same-origin P6 client', () => {
  it('sends exact mutation headers and validates project response', async () => {
    const mock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ metadata, state: {} }), { status: 201 }));
    vi.stubGlobal('fetch', mock);
    expect((await createProject('Studio')).metadata.name).toBe('Studio');
    const [url, init] = mock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('/api/v1/projects');
    expect(init.method).toBe('POST');
    expect(init.credentials).toBe('same-origin');
    expect(init.headers).toEqual({ 'X-Aurora-Request': '1', 'Content-Type': 'application/json' });
    expect(init.body).toBe('{"name":"Studio"}');
  });

  it('sends the exact P7 editor body and last saved timestamp', async () => {
    const editor = blankEditor('Studio', 'en');
    const mock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ metadata, state: { editor } })));
    vi.stubGlobal('fetch', mock);
    await saveEditor(id, editor, 'then');
    const body = JSON.parse((mock.mock.calls[0] as [string, RequestInit])[1].body as string) as Record<string, unknown>;
    expect(body).toEqual({ editor, expected_updated_at: 'then' });
  });

  it('does not accept a malformed editor response as a successful save', async () => {
    const editor = blankEditor('Studio', 'en');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ metadata, state: { editor: { schema_version: 2 } } }))));
    await expect(saveEditor(id, editor, 'then')).rejects.toThrow('Unsupported editor state');
  });

  it('rejects malformed API success and uses only numeric errors', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{"error":{"code":409,"raw":"private"}}', { status: 409 })));
    await expect(createProject('A')).rejects.toMatchObject({ status: 409 });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{"unexpected":"private"}', { status: 201 })));
    await expect(createProject('A')).rejects.toThrow('Invalid project response');
  });

  it('keeps secrets in only the explicit credential body', async () => {
    const mock = vi.fn().mockResolvedValueOnce(new Response('{"configured":false}'))
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', mock);
    expect(await credentialStatus('openai_api_key')).toBe(false);
    await setCredential('openai_api_key', 'test-secret');
    expect((mock.mock.calls[1] as [string, RequestInit])[1].body).toBe('{"secret":"test-secret"}');
    expect((mock.mock.calls[0] as [string, RequestInit])[1].headers).toEqual({});
  });

  it('sends raster bytes, never multipart or user filename', async () => {
    const path = `assets/${'a'.repeat(64)}.png`;
    const mock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ path }), { status: 201 }));
    vi.stubGlobal('fetch', mock);
    const file = new File([new Uint8Array([137, 80, 78, 71])], 'private.png', { type: 'image/png' });
    expect(await uploadRaster(id, file)).toBe(path);
    const [url, init] = mock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`/api/v1/projects/${id}/assets`);
    expect(init.body).toBe(file);
    expect(init.headers).toEqual({ 'X-Aurora-Request': '1', 'Content-Type': 'image/png' });
    await expect(uploadRaster(id, new File(['x'], 'x.svg', { type: 'image/svg+xml' }))).rejects.toThrow();
  });

  it('parses terminal text, ZIP and deploy recovery without retry', async () => {
    const mock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({
      job_id: id, status: 'completed', result: { response_id: 'r', model: 'm', output_text: 'Hello' }, failure: null,
    }))).mockResolvedValueOnce(new Response('zip', { headers: { 'content-type': 'application/zip' } }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ error: { code: 503, recovery: { site_id: id, deploy_id: null } } }), { status: 503 }));
    vi.stubGlobal('fetch', mock);
    expect((await generateText('m', 'prompt', 'instruction')).result?.output_text).toBe('Hello');
    expect((await exportZip(id, 'then')).size).toBe(3);
    try { await deployNetlify(id, 'then', null); } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).recovery).toEqual({ site_id: id, deploy_id: null });
    }
    expect(mock).toHaveBeenCalledTimes(3);
    expect(JSON.parse((mock.mock.calls[2] as [string, RequestInit])[1].body as string)).toEqual({
      expected_updated_at: 'then', confirm_deploy: true, site_id: null,
    });
  });
});
