export type Language = 'ru' | 'en';
export interface UserPreferences {
  schema_version: 1;
  language: Language | null;
  general_model: string;
  image_model: string;
  onboarding_completed: boolean;
}

export interface PreferencesSnapshot {
  preferences: UserPreferences;
  revision: string;
  projects_directory: string;
}
export type FontFamily = 'system' | 'serif' | 'monospace';

export interface EditorBrand {
  name: string;
  tagline: string;
  primary_color: string;
  secondary_color: string;
  font_family: FontFamily;
  logo_path: string | null;
}

export interface EditorSection {
  id: string;
  heading: string;
  body: string;
  image_path: string | null;
  image_alt: string;
}

export interface EditorPage {
  id: string;
  slug: string;
  title: string;
  meta_description: string;
  heading: string;
  sections: EditorSection[];
}

export interface EditorDocument {
  schema_version: 1;
  language: Language;
  brand: EditorBrand;
  pages: EditorPage[];
}

export interface ProjectMetadata {
  project_id: string;
  name: string;
  format_version: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDocument {
  metadata: ProjectMetadata;
  state: Record<string, unknown>;
}

export interface TextResult {
  job_id: string;
  status: 'completed' | 'failed';
  result: { response_id: string; model: string; output_text: string } | null;
  failure: { category: string; message: string; retryable: boolean } | null;
}

export type DraftFailureCategory = 'authentication' | 'rate_limited' | 'remote' | 'network' | 'invalid_response';
export type ImageResult =
  | { job_id: string; status: 'completed'; source_updated_at: string; asset_path: string; failure: null }
  | { job_id: string; status: 'failed'; source_updated_at: string; asset_path: null;
      failure: { category: DraftFailureCategory; message: string; retryable: boolean } };
export type DraftResult =
  | { job_id: string; status: 'completed'; source_updated_at: string; editor: EditorDocument; failure: null }
  | { job_id: string; status: 'failed'; source_updated_at: string; editor: null;
      failure: { category: DraftFailureCategory; message: string; retryable: boolean } };

export interface DeploymentResult {
  site_id: string;
  deploy_id: string;
  public_url: string;
}

export function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function keys(value: Record<string, unknown>, expected: string[]): boolean {
  return Object.keys(value).length === expected.length && expected.every((key) => key in value);
}

export function parseUserPreferences(value: unknown): UserPreferences {
  if (!record(value) || !keys(value, ['schema_version', 'language', 'general_model', 'image_model', 'onboarding_completed']) ||
      value.schema_version !== 1 || (value.language !== null && value.language !== 'ru' && value.language !== 'en') ||
      !validPreferenceModel(value.general_model) || !validPreferenceModel(value.image_model) ||
      typeof value.onboarding_completed !== 'boolean') {
    throw new Error('Invalid preferences response');
  }
  return value as unknown as UserPreferences;
}

export function validPreferenceModel(value: unknown): value is string {
  if (typeof value !== 'string' || !value.trim() || /\p{Cc}/u.test(value)) return false;
  try { encodeURIComponent(value); return true; } catch { return false; }
}

export function parsePreferencesSnapshot(value: unknown): PreferencesSnapshot {
  if (!record(value) || !keys(value, ['preferences', 'revision', 'projects_directory']) ||
      typeof value.revision !== 'string' || !/^[0-9a-f]{64}$/.test(value.revision) ||
      typeof value.projects_directory !== 'string' ||
      !/^(?:[A-Za-z]:[\\/]|\/|\\\\)/.test(value.projects_directory) ||
      /\p{Cc}/u.test(value.projects_directory)) {
    throw new Error('Invalid preferences response');
  }
  return { preferences: parseUserPreferences(value.preferences), revision: value.revision,
    projects_directory: value.projects_directory };
}

export function parseSavedPreferences(value: unknown): { preferences: UserPreferences; revision: string } {
  if (!record(value) || !keys(value, ['preferences', 'revision']) ||
      typeof value.revision !== 'string' || !/^[0-9a-f]{64}$/.test(value.revision)) {
    throw new Error('Invalid preferences response');
  }
  return { preferences: parseUserPreferences(value.preferences), revision: value.revision };
}

function uuid(value: unknown): value is string {
  return typeof value === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value);
}

function nullableString(value: unknown): value is string | null {
  return value === null || typeof value === 'string';
}

export function parseMetadata(value: unknown): ProjectMetadata {
  if (!record(value) || !keys(value, ['project_id', 'name', 'format_version', 'created_at', 'updated_at']) ||
      !uuid(value.project_id) || typeof value.name !== 'string' || typeof value.format_version !== 'string' ||
      typeof value.created_at !== 'string' || typeof value.updated_at !== 'string') {
    throw new Error('Invalid project metadata');
  }
  return value as unknown as ProjectMetadata;
}

export function parseProject(value: unknown): ProjectDocument {
  if (!record(value) || !keys(value, ['metadata', 'state']) || !record(value.state)) {
    throw new Error('Invalid project response');
  }
  return { metadata: parseMetadata(value.metadata), state: value.state };
}

export function parseEditor(value: unknown): EditorDocument {
  if (!record(value) || !keys(value, ['schema_version', 'language', 'brand', 'pages']) ||
      value.schema_version !== 1 || (value.language !== 'ru' && value.language !== 'en') ||
      !record(value.brand) || !Array.isArray(value.pages)) {
    throw new Error('Unsupported editor state');
  }
  const brand = value.brand;
  if (!keys(brand, ['name', 'tagline', 'primary_color', 'secondary_color', 'font_family', 'logo_path']) ||
      typeof brand.name !== 'string' || typeof brand.tagline !== 'string' ||
      typeof brand.primary_color !== 'string' || typeof brand.secondary_color !== 'string' ||
      (brand.font_family !== 'system' && brand.font_family !== 'serif' && brand.font_family !== 'monospace') || !nullableString(brand.logo_path)) {
    throw new Error('Unsupported editor state');
  }
  const pageIds = new Set<string>();
  const sectionIds = new Set<string>();
  for (const page of value.pages) {
    if (!record(page) || !keys(page, ['id', 'slug', 'title', 'meta_description', 'heading', 'sections']) ||
        !uuid(page.id) || pageIds.has(page.id) || typeof page.slug !== 'string' ||
        typeof page.title !== 'string' || typeof page.meta_description !== 'string' ||
        typeof page.heading !== 'string' || !Array.isArray(page.sections)) {
      throw new Error('Unsupported editor state');
    }
    pageIds.add(page.id);
    for (const section of page.sections) {
      if (!record(section) || !keys(section, ['id', 'heading', 'body', 'image_path', 'image_alt']) ||
          !uuid(section.id) || sectionIds.has(section.id) || typeof section.heading !== 'string' ||
          typeof section.body !== 'string' || !nullableString(section.image_path) ||
          typeof section.image_alt !== 'string') {
        throw new Error('Unsupported editor state');
      }
      sectionIds.add(section.id);
    }
  }
  return value as unknown as EditorDocument;
}

export function parseTextResult(value: unknown): TextResult {
  if (!record(value) || !uuid(value.job_id) || (value.status !== 'completed' && value.status !== 'failed')) {
    throw new Error('Invalid generation response');
  }
  if (value.status === 'completed') {
    if (!record(value.result) || typeof value.result.response_id !== 'string' ||
        typeof value.result.model !== 'string' || typeof value.result.output_text !== 'string' || value.failure !== null) {
      throw new Error('Invalid generation response');
    }
  } else if (!record(value.failure) || typeof value.failure.category !== 'string' ||
             typeof value.failure.message !== 'string' || typeof value.failure.retryable !== 'boolean' || value.result !== null) {
    throw new Error('Invalid generation response');
  }
  return value as unknown as TextResult;
}

export function validDraftInputs(name: string, prompt: string, model: string): boolean {
  try {
    encodeURIComponent(name); encodeURIComponent(prompt); encodeURIComponent(model);
    const encoder = new TextEncoder();
    return !!name.trim() && encoder.encode(name).length <= 256 &&
      !!prompt.trim() && encoder.encode(prompt).length <= 8 * 1024 && !!model.trim();
  } catch { return false; }
}

export function parseDraftResult(value: unknown, expected: string, language: Language): DraftResult {
  if (!record(value) || !keys(value, ['job_id', 'status', 'source_updated_at', 'editor', 'failure']) ||
      !uuid(value.job_id) || value.source_updated_at !== expected) {
    throw new Error('Invalid project draft response');
  }
  if (value.status === 'completed') {
    if (value.failure !== null) throw new Error('Invalid project draft response');
    const editor = parseEditor(value.editor);
    if (editor.language !== language) throw new Error('Invalid project draft response');
    return { job_id: value.job_id, status: 'completed', source_updated_at: expected, editor, failure: null };
  }
  if (value.status === 'failed' && value.editor === null && record(value.failure) &&
      keys(value.failure, ['category', 'message', 'retryable']) &&
      typeof value.failure.category === 'string' &&
      ['authentication', 'rate_limited', 'remote', 'network', 'invalid_response'].includes(value.failure.category) &&
      typeof value.failure.message === 'string' && typeof value.failure.retryable === 'boolean') {
    return { job_id: value.job_id, status: 'failed', source_updated_at: expected, editor: null,
      failure: { category: value.failure.category as DraftFailureCategory,
        message: value.failure.message, retryable: value.failure.retryable } };
  }
  throw new Error('Invalid project draft response');
}

export function validImageInputs(prompt: string, model: string): boolean {
  try {
    encodeURIComponent(prompt); encodeURIComponent(model);
    const encoder = new TextEncoder();
    return !!prompt.trim() && encoder.encode(prompt).length <= 8 * 1024 && !!model.trim();
  } catch { return false; }
}

export function parseImageResult(value: unknown, expected: string): ImageResult {
  if (!record(value) || !keys(value, ['job_id', 'status', 'source_updated_at', 'asset_path', 'failure']) ||
      !uuid(value.job_id) || value.source_updated_at !== expected) {
    throw new Error('Invalid image generation response');
  }
  if (value.status === 'completed' && value.failure === null &&
      typeof value.asset_path === 'string' && /^assets\/[a-f0-9]{64}\.png$/.test(value.asset_path)) {
    return { job_id: value.job_id, status: 'completed', source_updated_at: expected,
      asset_path: value.asset_path, failure: null };
  }
  if (value.status === 'failed' && value.asset_path === null && record(value.failure) &&
      keys(value.failure, ['category', 'message', 'retryable']) &&
      typeof value.failure.category === 'string' &&
      ['authentication', 'rate_limited', 'remote', 'network', 'invalid_response'].includes(value.failure.category) &&
      typeof value.failure.message === 'string' && typeof value.failure.retryable === 'boolean') {
    return { job_id: value.job_id, status: 'failed', source_updated_at: expected, asset_path: null,
      failure: { category: value.failure.category as DraftFailureCategory,
        message: value.failure.message, retryable: value.failure.retryable } };
  }
  throw new Error('Invalid image generation response');
}

export function parseDeployment(value: unknown): DeploymentResult {
  if (!record(value) || !keys(value, ['site_id', 'deploy_id', 'public_url']) ||
      !uuid(value.site_id) || !uuid(value.deploy_id) || typeof value.public_url !== 'string' ||
      !/^https:\/\//.test(value.public_url)) {
    throw new Error('Invalid deployment response');
  }
  return value as unknown as DeploymentResult;
}
