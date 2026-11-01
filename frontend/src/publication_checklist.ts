import type { EditorDocument } from './types';

export type PublicationGapKind =
  | 'brandName' | 'noPages' | 'pageTitle' | 'pageHeading' | 'metaDescription'
  | 'noSections' | 'sectionHeading' | 'sectionBody' | 'imageAlt';

export interface PublicationGap {
  readonly kind: PublicationGapKind;
  readonly page: number | null;
  readonly section: number | null;
}

export interface PublicationChecklist {
  readonly total: number;
  readonly shown: readonly PublicationGap[];
}

const MAX_SHOWN = 20;

export function publicationChecklist(editor: EditorDocument): PublicationChecklist {
  const shown: PublicationGap[] = [];
  let total = 0;
  const add = (kind: PublicationGapKind, page: number | null = null, section: number | null = null) => {
    total += 1;
    if (shown.length < MAX_SHOWN) shown.push(Object.freeze({ kind, page, section }));
  };

  if (!editor.brand.name.trim()) add('brandName');
  if (editor.pages.length === 0) add('noPages');
  editor.pages.forEach((page, pageIndex) => {
    const position = pageIndex + 1;
    if (!page.title.trim()) add('pageTitle', position);
    if (!page.heading.trim()) add('pageHeading', position);
    if (!page.meta_description.trim()) add('metaDescription', position);
    if (page.sections.length === 0) add('noSections', position);
    page.sections.forEach((section, sectionIndex) => {
      const item = sectionIndex + 1;
      if (!section.heading.trim()) add('sectionHeading', position, item);
      if (!section.body.trim()) add('sectionBody', position, item);
      if (section.image_path !== null && !section.image_alt.trim()) add('imageAlt', position, item);
    });
  });

  return Object.freeze({ total, shown: Object.freeze(shown) });
}
