import { describe, expect, it } from 'vitest';
import { preparedSitePrompt, preparedSitePromptWithBrief } from '../src/prepared_site_prompt';
import { parseEditor } from '../src/types';
import type { Language } from '../src/types';

describe('UI-010 preparation prompt', () => {
  it.each<Language>(['ru', 'en'])('contains a valid text-only P7 v1 example for %s', (language) => {
    const prompt = preparedSitePrompt(language);
    const start = prompt.indexOf('{\n');
    const end = prompt.indexOf('\n}\n', start);
    expect(start).toBeGreaterThan(-1);
    expect(end).toBeGreaterThan(start);
    const example = parseEditor(JSON.parse(prompt.slice(start, end + 2)) as unknown);
    expect(example.schema_version).toBe(1);
    expect(example.language).toBe(language);
    expect(example.pages).toHaveLength(1);
    expect(example.pages[0]?.slug).toBe('index');
    expect(example.pages[0]?.id).not.toBe(example.pages[0]?.sections[0]?.id);
    expect(example.brand.logo_path).toBeNull();
    expect(example.pages[0]?.sections[0]?.image_path).toBeNull();
    expect(prompt).toContain('Return ONLY a UTF-8 JSON object, without Markdown');
    expect(prompt).toContain('never reuse the sample IDs');
    expect(prompt).toContain('1–8 pages');
    expect(prompt).toContain('1–12 sections');
    expect(prompt).toContain('Do not include credentials');
  });
});

describe('UI-017 preparation prompt with brief', () => {
  it.each<Language>(['ru', 'en'])('replaces the one placeholder for %s without changing the template rules', (language) => {
    const brief = '  Customer studio\nwith two locations  ';
    const result = preparedSitePromptWithBrief(language, brief);
    expect(result).toContain('Business brief:\nCustomer studio\nwith two locations');
    expect(result).not.toContain('[Insert only the brief');
    expect(result.split('Customer studio').length - 1).toBe(1);
    expect(result).toContain(`"language": "${language}"`);
    expect(result).toContain('Do not include credentials');
  });
});
