import { describe, expect, it } from 'vitest';
import { blankEditor } from '../src/editor';
import { ImportValidationError, MAX_IMPORT_BYTES, readPreparedEditor, sameEditor } from '../src/project_import';

const encoder = new TextEncoder();

function file(bytes: Uint8Array): File {
  const selected = new File([Uint8Array.from(bytes).buffer], 'site.txt', { type: 'text/plain' });
  Object.defineProperty(selected, 'arrayBuffer', { configurable: true,
    value: async () => Uint8Array.from(bytes).buffer });
  return selected;
}

function json(value: unknown): File { return file(encoder.encode(JSON.stringify(value))); }

async function fails(selected: File, reason: ImportValidationError['reason']) {
  await expect(readPreparedEditor(selected)).rejects.toMatchObject({ reason });
}

describe('UI-007 local text-only import boundary', () => {
  it('accepts a valid editor regardless of filename/MIME and permits exactly 1 MiB', async () => {
    const editor = blankEditor('Studio', 'ru');
    expect(await readPreparedEditor(json(editor))).toEqual(editor);
    const payload = JSON.stringify(editor);
    const padded = file(encoder.encode(payload + ' '.repeat(MAX_IMPORT_BYTES - encoder.encode(payload).length)));
    expect(padded.size).toBe(MAX_IMPORT_BYTES);
    expect(await readPreparedEditor(padded)).toEqual(editor);
    await fails(file(encoder.encode(payload + ' '.repeat(MAX_IMPORT_BYTES - encoder.encode(payload).length + 1))), 'size');
  });

  it('rejects unreadable bytes, invalid UTF-8 and invalid JSON without exposing content', async () => {
    await fails(file(new Uint8Array([0xc3, 0x28])), 'encoding');
    await fails(file(encoder.encode('{"secret":"never echo"')), 'json');
    const unreadable = json(blankEditor('Studio', 'en'));
    Object.defineProperty(unreadable, 'arrayBuffer', { value: async () => { throw new Error('private'); } });
    await fails(unreadable, 'read');
  });

  it('rejects unsupported schema, unknown keys, malformed and duplicate IDs', async () => {
    const editor = blankEditor('Studio', 'en');
    await fails(json({ ...editor, schema_version: 2 }), 'schema');
    await fails(json({ ...editor, unexpected: 'data' }), 'schema');
    await fails(json({ ...editor, pages: [{ ...editor.pages[0], id: 'INVALID' }] }), 'schema');
    await fails(json({ ...editor, pages: [editor.pages[0], editor.pages[0]] }), 'schema');
    const first = editor.pages[0]?.sections[0];
    await fails(json({ ...editor, pages: [{ ...editor.pages[0], sections: [first, first] }] }), 'schema');
  });

  it('rejects claims to assets not imported with the file', async () => {
    const editor = blankEditor('Studio', 'en');
    await fails(json({ ...editor, brand: { ...editor.brand, logo_path: 'assets/logo.png' } }), 'assets');
    await fails(json({ ...editor, pages: [{ ...editor.pages[0], sections: [
      { ...editor.pages[0]?.sections[0], image_path: 'assets/photo.png' },
    ] }] }), 'assets');
  });

  it('compares every persisted editor field, not object key order', () => {
    const editor = blankEditor('Studio', 'en');
    expect(sameEditor(editor, JSON.parse(JSON.stringify(editor)) as typeof editor)).toBe(true);
    const altered = JSON.parse(JSON.stringify(editor)) as typeof editor;
    altered.pages[0]!.sections[0]!.body = 'Changed';
    expect(sameEditor(editor, altered)).toBe(false);
  });
});
