import type { EditorBrand, EditorDocument } from './types';

export const BRAND_PRESET_IDS = Object.freeze(['indigo', 'ocean', 'forest', 'warm'] as const);
export type BrandPresetId = typeof BRAND_PRESET_IDS[number];

type BrandStyle = Pick<EditorBrand, 'primary_color' | 'secondary_color' | 'font_family'>;

const PRESETS = Object.freeze({
  indigo: Object.freeze({ primary_color: '#4F46E5', secondary_color: '#0F172A', font_family: 'system' }),
  ocean: Object.freeze({ primary_color: '#075985', secondary_color: '#0C4A6E', font_family: 'system' }),
  forest: Object.freeze({ primary_color: '#166534', secondary_color: '#14532D', font_family: 'serif' }),
  warm: Object.freeze({ primary_color: '#9A3412', secondary_color: '#7C2D12', font_family: 'serif' }),
} as const satisfies Record<BrandPresetId, BrandStyle>);

function presetFor(id: BrandPresetId): BrandStyle {
  if (!Object.hasOwn(PRESETS, id)) throw new Error('Invalid brand preset');
  return PRESETS[id];
}

export function brandPresetMatches(brand: EditorBrand, id: BrandPresetId): boolean {
  const preset = presetFor(id);
  return brand.primary_color === preset.primary_color &&
    brand.secondary_color === preset.secondary_color &&
    brand.font_family === preset.font_family;
}

export function applyBrandPreset(editor: EditorDocument, id: BrandPresetId): EditorDocument {
  const preset = presetFor(id);
  if (brandPresetMatches(editor.brand, id)) return editor;
  return { ...editor, brand: { ...editor.brand, ...preset } };
}
