import { describe, expect, it } from 'vitest';
import { assetName, blankEditor, move, nextPageSlug, replacePage, replaceSection } from '../src/editor';
import { parseEditor, parseMetadata, parseProject } from '../src/types';

describe('P7 editor boundary', () => {
  it('makes exactly the approved blank v1 shape in RU and EN', () => {
    const ru = blankEditor('Бизнес', 'ru');
    expect(ru).toEqual({
      schema_version: 1, language: 'ru',
      brand: { name: 'Бизнес', tagline: '', primary_color: '#4F46E5', secondary_color: '#0F172A', font_family: 'system', logo_path: null },
      pages: [{ id: expect.any(String), slug: 'index', title: 'Бизнес', meta_description: '', heading: 'Бизнес',
        sections: [{ id: expect.any(String), heading: 'О нас', body: '', image_path: null, image_alt: '' }] }],
    });
    expect(parseEditor(ru)).toEqual(ru);
    expect(blankEditor('Studio', 'en').pages[0]?.sections[0]?.heading).toBe('About');
  });

  it('rejects unknown and malformed editor schema rather than migrating', () => {
    const editor = blankEditor('A', 'en');
    expect(() => parseEditor({ ...editor, schema_version: 2 })).toThrow();
    expect(() => parseEditor({ ...editor, extra: true })).toThrow();
    expect(() => parseEditor({ ...editor, brand: { ...editor.brand, font_family: 4 } })).toThrow();
    expect(() => parseEditor({ ...editor, pages: [editor.pages[0], editor.pages[0]] })).toThrow();
    expect(() => parseEditor(null)).toThrow();
  });

  it('validates metadata and preserves opaque outer state', () => {
    const metadata = { project_id: crypto.randomUUID(), name: 'A', format_version: '1', created_at: 'now', updated_at: 'now' };
    const state = { custom: { untouched: true } };
    expect(parseMetadata(metadata)).toEqual(metadata);
    expect(parseProject({ metadata, state }).state).toEqual(state);
    expect(() => parseProject({ metadata, state: null })).toThrow();
  });

  it('performs immutable page, section and ordering edits', () => {
    const editor = blankEditor('A', 'en');
    const page = editor.pages[0]!;
    const section = page.sections[0]!;
    const changed = replaceSection(editor, page.id, { ...section, body: 'New' });
    expect(editor.pages[0]?.sections[0]?.body).toBe('');
    expect(changed.pages[0]?.sections[0]?.body).toBe('New');
    expect(replacePage(editor, { ...page, title: 'B' }).pages[0]?.title).toBe('B');
    expect(move(['a', 'b'], 0, 1)).toEqual(['b', 'a']);
    expect(move(['a'], 0, 1)).toEqual(['a']);
    expect(nextPageSlug(editor)).toBe('page-1');
    expect(assetName(`assets/${'a'.repeat(64)}.png`)).toBe(`${'a'.repeat(64)}.png`);
    expect(assetName('../secret')).toBeNull();
  });
});
