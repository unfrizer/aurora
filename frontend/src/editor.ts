import type { EditorDocument, EditorPage, EditorSection, Language } from './types';

export function blankEditor(name: string, language: Language): EditorDocument {
  return {
    schema_version: 1,
    language,
    brand: {
      name,
      tagline: '',
      primary_color: '#4F46E5',
      secondary_color: '#0F172A',
      font_family: 'system',
      logo_path: null,
    },
    pages: [{
      id: crypto.randomUUID(), slug: 'index', title: name, meta_description: '', heading: name,
      sections: [{ id: crypto.randomUUID(), heading: language === 'ru' ? 'О нас' : 'About',
        body: '', image_path: null, image_alt: '' }],
    }],
  };
}

export function replacePage(editor: EditorDocument, page: EditorPage): EditorDocument {
  return { ...editor, pages: editor.pages.map((item) => item.id === page.id ? page : item) };
}

export function replaceSection(editor: EditorDocument, pageId: string, section: EditorSection): EditorDocument {
  return { ...editor, pages: editor.pages.map((page) => page.id === pageId
    ? { ...page, sections: page.sections.map((item) => item.id === section.id ? section : item) }
    : page) };
}

export function move<T>(items: T[], index: number, delta: number): T[] {
  const destination = index + delta;
  if (index < 0 || destination < 0 || index >= items.length || destination >= items.length) return items;
  const result = [...items];
  const [item] = result.splice(index, 1);
  if (item === undefined) return items;
  result.splice(destination, 0, item);
  return result;
}

export function nextPageSlug(editor: EditorDocument): string {
  let index = 1;
  while (editor.pages.some((page) => page.slug === `page-${index}`)) index += 1;
  return `page-${index}`;
}

export function assetName(path: string): string | null {
  const match = /^assets\/([a-f0-9]{64}\.(?:png|jpg|gif|webp))$/.exec(path);
  return match?.[1] ?? null;
}
