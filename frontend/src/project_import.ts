import { parseEditor } from './types';
import type { EditorDocument } from './types';

export const MAX_IMPORT_BYTES = 1024 * 1024;

export type ImportFailure = 'size' | 'encoding' | 'json' | 'schema' | 'assets' | 'read';

export class ImportValidationError extends Error {
  constructor(public readonly reason: ImportFailure) {
    super(`Invalid prepared site: ${reason}`);
  }
}

export async function readPreparedEditor(file: File): Promise<EditorDocument> {
  if (file.size > MAX_IMPORT_BYTES) throw new ImportValidationError('size');

  let bytes: ArrayBuffer;
  try { bytes = await file.arrayBuffer(); }
  catch { throw new ImportValidationError('read'); }
  if (bytes.byteLength > MAX_IMPORT_BYTES) throw new ImportValidationError('size');

  let text: string;
  try { text = new TextDecoder('utf-8', { fatal: true }).decode(bytes); }
  catch { throw new ImportValidationError('encoding'); }

  let value: unknown;
  try { value = JSON.parse(text) as unknown; }
  catch { throw new ImportValidationError('json'); }

  let editor: EditorDocument;
  try { editor = parseEditor(value); }
  catch { throw new ImportValidationError('schema'); }

  if (editor.brand.logo_path !== null || editor.pages.some((page) =>
    page.sections.some((section) => section.image_path !== null))) {
    throw new ImportValidationError('assets');
  }
  return editor;
}

export function sameEditor(left: EditorDocument, right: EditorDocument): boolean {
  return left.schema_version === right.schema_version && left.language === right.language &&
    left.brand.name === right.brand.name && left.brand.tagline === right.brand.tagline &&
    left.brand.primary_color === right.brand.primary_color && left.brand.secondary_color === right.brand.secondary_color &&
    left.brand.font_family === right.brand.font_family && left.brand.logo_path === right.brand.logo_path &&
    left.pages.length === right.pages.length && left.pages.every((page, index) => {
      const savedPage = right.pages[index];
      return savedPage !== undefined && page.id === savedPage.id && page.slug === savedPage.slug &&
        page.title === savedPage.title && page.meta_description === savedPage.meta_description &&
        page.heading === savedPage.heading && page.sections.length === savedPage.sections.length &&
        page.sections.every((section, sectionIndex) => {
          const savedSection = savedPage.sections[sectionIndex];
          return savedSection !== undefined && section.id === savedSection.id &&
            section.heading === savedSection.heading && section.body === savedSection.body &&
            section.image_path === savedSection.image_path && section.image_alt === savedSection.image_alt;
        });
    });
}
