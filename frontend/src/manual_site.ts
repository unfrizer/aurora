import { blankEditor } from './editor';
import type { EditorDocument, Language } from './types';

export interface ManualSiteInput {
  name: string;
  tagline: string;
  headline: string;
  sectionHeading: string;
  body: string;
  metaDescription: string;
  servicesBody?: string;
  contactBody?: string;
}

export function validManualSite(input: ManualSiteInput): boolean {
  const encoder = new TextEncoder();
  const within = (value: string, limit: number, required: boolean): boolean => {
    if (typeof value !== 'string') return false;
    try {
      encodeURIComponent(value);
      return (!required || !!value.trim()) && encoder.encode(value).length <= limit;
    } catch { return false; }
  };
  return within(input.name, 256, true) && within(input.tagline, 256, false) &&
    within(input.headline, 256, true) && within(input.sectionHeading, 256, true) &&
    within(input.body, 8 * 1024, true) && within(input.metaDescription, 320, false) &&
    within(input.servicesBody === undefined ? '' : input.servicesBody, 8 * 1024, false) &&
    within(input.contactBody === undefined ? '' : input.contactBody, 8 * 1024, false);
}

export function manualSiteStarter(input: ManualSiteInput, language: Language): EditorDocument {
  if (!validManualSite(input)) throw new Error('Invalid manual site input');
  const initial = blankEditor(input.name.trim(), language);
  const firstPage = initial.pages[0];
  const firstSection = firstPage?.sections[0];
  if (!firstPage || !firstSection) throw new Error('Invalid blank editor');
  const pages: EditorDocument['pages'] = [{
    ...firstPage,
    heading: input.headline,
    meta_description: input.metaDescription,
    sections: [{ ...firstSection, heading: input.sectionHeading, body: input.body }],
  }];
  const addPage = (slug: string, heading: string, body: string) => {
    if (!body.trim()) return;
    pages.push({
      id: crypto.randomUUID(), slug, title: `${input.name.trim()} — ${heading}`,
      meta_description: '', heading,
      sections: [{ ...firstSection, id: crypto.randomUUID(), heading, body }],
    });
  };
  addPage('services', language === 'ru' ? 'Услуги' : 'Services', input.servicesBody ?? '');
  addPage('contact', language === 'ru' ? 'Контакты' : 'Contact', input.contactBody ?? '');
  return {
    ...initial,
    brand: { ...initial.brand, tagline: input.tagline },
    pages,
  };
}
