export type Language = 'ru' | 'en';
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

export function parseDeployment(value: unknown): DeploymentResult {
  if (!record(value) || !keys(value, ['site_id', 'deploy_id', 'public_url']) ||
      !uuid(value.site_id) || !uuid(value.deploy_id) || typeof value.public_url !== 'string' ||
      !/^https:\/\//.test(value.public_url)) {
    throw new Error('Invalid deployment response');
  }
  return value as unknown as DeploymentResult;
}
