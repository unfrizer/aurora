import { blankEditor } from './editor';
import type { EditorDocument, Language } from './types';

export function validOfflineBrief(name: string, brief: string): boolean {
  try {
    encodeURIComponent(name);
    encodeURIComponent(brief);
    const encoder = new TextEncoder();
    return !!name.trim() && encoder.encode(name).length <= 256 &&
      !!brief.trim() && encoder.encode(brief).length <= 8 * 1024;
  } catch { return false; }
}

export function offlineStarter(name: string, language: Language, brief: string): EditorDocument {
  if (!validOfflineBrief(name, brief)) throw new Error('Invalid offline starter input');
  const initial = blankEditor(name.trim(), language);
  const firstPage = initial.pages[0];
  const firstSection = firstPage?.sections[0];
  if (!firstPage || !firstSection) throw new Error('Invalid blank editor');
  return { ...initial, pages: initial.pages.map((page, pageIndex) => pageIndex === 0
    ? { ...page, sections: page.sections.map((section, sectionIndex) => sectionIndex === 0
      ? { ...section, body: brief } : section) }
    : page) };
}
