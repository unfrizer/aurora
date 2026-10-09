import { MAX_RASTER_BYTES, RASTER_TYPES } from './config';
import {
  parseDeployment, parseEditor, parseMetadata, parseProject, parseTextResult, record,
  type DeploymentResult, type EditorDocument, type ProjectDocument, type ProjectMetadata, type TextResult,
} from './types';

const ROOT = '/api/v1';
type CredentialName = 'openai_api_key' | 'netlify_token';
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

export class ApiError extends Error {
  constructor(public readonly status: number, public readonly recovery: { site_id: string | null; deploy_id: string | null } | null = null) {
    super(`API error ${status}`);
  }
}

async function failure(response: Response): Promise<never> {
  let value: unknown;
  try { value = await response.json() as unknown; } catch { throw new ApiError(response.status); }
  if (!record(value) || !record(value.error) || value.error.code !== response.status) {
    throw new ApiError(response.status);
  }
  const maybe = value.error.recovery;
  if (record(maybe) && Object.keys(maybe).length === 2 &&
      (maybe.site_id === null || (typeof maybe.site_id === 'string' && UUID.test(maybe.site_id))) &&
      (maybe.deploy_id === null || (typeof maybe.deploy_id === 'string' && UUID.test(maybe.deploy_id)))) {
    throw new ApiError(response.status, { site_id: maybe.site_id, deploy_id: maybe.deploy_id });
  }
  throw new ApiError(response.status);
}

async function request(path: string, method = 'GET', body?: unknown, contentType = 'application/json'): Promise<Response> {
  const mutating = method !== 'GET';
  const headers: Record<string, string> = {};
  if (mutating) headers['X-Aurora-Request'] = '1';
  if (body !== undefined) headers['Content-Type'] = contentType;
  const response = await fetch(`${ROOT}${path}`, {
    method, headers, credentials: 'same-origin', cache: 'no-store',
    body: body === undefined ? undefined : body instanceof Blob ? body : JSON.stringify(body),
  });
  if (!response.ok) return failure(response);
  return response;
}

async function json(path: string, method = 'GET', body?: unknown): Promise<unknown> {
  const response = await request(path, method, body);
  return await response.json() as unknown;
}

const projectPath = (id: string): string => `/projects/${encodeURIComponent(id)}`;

export async function listProjects(): Promise<ProjectMetadata[]> {
  const value = await json('/projects');
  if (!Array.isArray(value)) throw new Error('Invalid projects response');
  return value.map(parseMetadata);
}

export async function createProject(name: string): Promise<ProjectDocument> {
  return parseProject(await json('/projects', 'POST', { name }));
}

export async function openProject(id: string): Promise<ProjectDocument> {
  return parseProject(await json(projectPath(id)));
}

export async function saveEditor(id: string, editor: EditorDocument, expected: string): Promise<ProjectDocument> {
  const saved = parseProject(await json(`${projectPath(id)}/editor`, 'PUT', { editor, expected_updated_at: expected }));
  parseEditor(saved.state.editor);
  return saved;
}

export async function renameProject(doc: ProjectDocument, name: string): Promise<ProjectDocument> {
  return parseProject(await json(projectPath(doc.metadata.project_id), 'PUT', {
    name, state: doc.state, expected_updated_at: doc.metadata.updated_at,
  }));
}

export async function deleteProject(id: string): Promise<void> {
  await request(projectPath(id), 'DELETE');
}

export async function credentialStatus(name: CredentialName): Promise<boolean> {
  const value = await json(`/credentials/${name}/status`);
  if (!record(value) || Object.keys(value).length !== 1 || typeof value.configured !== 'boolean') {
    throw new Error('Invalid credential status');
  }
  return value.configured;
}

export async function setCredential(name: CredentialName, secret: string): Promise<void> {
  await request(`/credentials/${name}`, 'PUT', { secret });
}

export async function deleteCredential(name: CredentialName): Promise<void> {
  await request(`/credentials/${name}`, 'DELETE');
}

export async function generateText(model: string, prompt: string, instructions: string): Promise<TextResult> {
  return parseTextResult(await json('/generation/text', 'POST', { model, prompt, instructions }));
}

export async function uploadRaster(projectId: string, file: File): Promise<string> {
  if (!RASTER_TYPES.some((type) => type === file.type) || !file.size || file.size > MAX_RASTER_BYTES) {
    throw new Error('Invalid raster');
  }
  const response = await request(`${projectPath(projectId)}/assets`, 'POST', file, file.type);
  const value = await response.json() as unknown;
  if (!record(value) || Object.keys(value).length !== 1 || typeof value.path !== 'string' ||
      !/^assets\/[a-f0-9]{64}\.(?:png|jpg|gif|webp)$/.test(value.path)) {
    throw new Error('Invalid asset response');
  }
  return value.path;
}

export async function deleteRaster(projectId: string, name: string): Promise<void> {
  if (!/^[a-f0-9]{64}\.(?:png|jpg|gif|webp)$/.test(name)) throw new Error('Invalid asset name');
  await request(`${projectPath(projectId)}/assets/${name}`, 'DELETE');
}

export function rasterUrl(projectId: string, path: string): string {
  const match = /^assets\/([a-f0-9]{64}\.(?:png|jpg|gif|webp))$/.exec(path);
  return match ? `${ROOT}${projectPath(projectId)}/assets/${match[1]}` : '';
}

export function previewUrl(projectId: string, slug = 'index'): string {
  if (!/^[a-z][a-z0-9-]{0,63}$/.test(slug)) return '';
  return `${ROOT}${projectPath(projectId)}/preview/${slug}.html`;
}

export async function exportZip(projectId: string, expected: string): Promise<Blob> {
  const response = await request(`${projectPath(projectId)}/exports/zip`, 'POST', { expected_updated_at: expected });
  if (!response.headers.get('content-type')?.startsWith('application/zip')) throw new Error('Invalid ZIP response');
  return response.blob();
}

export async function deployNetlify(projectId: string, expected: string, siteId: string | null): Promise<DeploymentResult> {
  return parseDeployment(await json(`${projectPath(projectId)}/deployments/netlify`, 'POST', {
    expected_updated_at: expected, confirm_deploy: true, site_id: siteId,
  }));
}
