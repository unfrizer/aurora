import type { EditorDocument, Language } from './types';

export function preparedSitePrompt(language: Language): string {
  const example: EditorDocument = {
    schema_version: 1,
    language,
    brand: {
      name: 'Brand name', tagline: 'Short tagline', primary_color: '#4F46E5',
      secondary_color: '#F59E0B', font_family: 'system', logo_path: null,
    },
    pages: [{
      id: '00000000-0000-4000-8000-000000000001', slug: 'index',
      title: 'Page SEO title', meta_description: 'Page meta description',
      heading: 'Visible page heading',
      sections: [{
        id: '00000000-0000-4000-8000-000000000002', heading: 'Section heading',
        body: 'Section text', image_path: null, image_alt: '',
      }],
    }],
  };
  return [
    'Prepare a text-only AURORA website draft from the business brief below.',
    'Return ONLY a UTF-8 JSON object, without Markdown, comments, HTML or code fences.',
    'Use exactly this structure and these field names; do not add other fields:',
    JSON.stringify(example, null, 2),
    'Replace all sample names, headings, text and SEO with meaningful content.',
    `Write the website content in ${language === 'ru' ? 'Russian' : 'English'}; keep the language field as "${language}".`,
    'Use 1–8 pages with exactly one "index" slug and 1–12 sections per page.',
    'Use a unique lowercase UUID for every page and section; never reuse the sample IDs.',
    'Other slugs must be distinct lowercase ASCII URL slugs.',
    'Keep logo_path and every image_path null even if photos are supplied separately.',
    'Use "system", "serif" or "monospace" for font_family and #RRGGBB colors.',
    'Do not include credentials, API keys or other secrets.',
    'Business brief:',
    '[Insert only the brief you are permitted to share with the external tool.]',
  ].join('\n');
}
