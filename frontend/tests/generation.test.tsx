import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProjectGeneration } from '../src/components/ProjectGeneration';
import { blankEditor } from '../src/editor';
import { parseDraftResult, validDraftInputs, type DraftResult } from '../src/types';

const id = '00000000-0000-4000-8000-000000000001';
const source = '2026-10-12T12:00:00Z';

describe('P6 project draft validation', () => {
  it('enforces UTF-8 byte limits without altering accepted input', () => {
    expect(validDraftInputs('Studio', '  Prompt  ', 'model')).toBe(true);
    expect(validDraftInputs(' ', 'Prompt', 'model')).toBe(false);
    expect(validDraftInputs('Studio', ' ', 'model')).toBe(false);
    expect(validDraftInputs('Studio', 'Prompt', ' ')).toBe(false);
    expect(validDraftInputs('a'.repeat(256), 'x', 'm')).toBe(true);
    expect(validDraftInputs('a'.repeat(257), 'x', 'm')).toBe(false);
    expect(validDraftInputs('😀'.repeat(64), 'x', 'm')).toBe(true);
    expect(validDraftInputs('😀'.repeat(65), 'x', 'm')).toBe(false);
    expect(validDraftInputs('A', 'é'.repeat(4096), 'm')).toBe(true);
    expect(validDraftInputs('A', 'é'.repeat(4097), 'm')).toBe(false);
    expect(validDraftInputs('A', '\ud800', 'm')).toBe(false);
  });

  it('accepts only exact terminal shapes and the requested language/source version', () => {
    const editor = blankEditor('Studio', 'ru');
    const completed = { job_id: id, status: 'completed', source_updated_at: source, editor, failure: null };
    const failed = { job_id: id, status: 'failed', source_updated_at: source, editor: null,
      failure: { category: 'network', message: 'Safe message', retryable: true } };
    expect(parseDraftResult(completed, source, 'ru').status).toBe('completed');
    expect(parseDraftResult(failed, source, 'ru').status).toBe('failed');
    for (const malformed of [
      { ...completed, extra: 'secret' },
      { ...completed, source_updated_at: 'stale' },
      { ...completed, failure: failed.failure },
      { ...completed, editor: { ...editor, schema_version: 2 } },
      { ...completed, job_id: 'bad' },
      { ...failed, failure: { ...failed.failure, retryable: 'yes' } },
      { ...failed, failure: { ...failed.failure, category: 'provider_secret' } },
      { ...failed, editor },
    ]) expect(() => parseDraftResult(malformed, source, 'ru')).toThrow();
    expect(() => parseDraftResult(completed, source, 'en')).toThrow();
  });

  it('renders generated text as text, never interpreted markup or a site preview', () => {
    const editor = blankEditor('Studio', 'en');
    editor.brand.tagline = '<img src=x onerror=alert(1)>';
    const candidate: Extract<DraftResult, { status: 'completed' }> = {
      job_id: id, status: 'completed', source_updated_at: source, editor, failure: null,
    };
    render(<ProjectGeneration language="en" projectName="Studio" model="m" prompt="private prompt"
      candidate={candidate} failure={null} pending={false} accepting={false} conflict={false}
      onPrompt={vi.fn()} onGenerate={vi.fn()} onAccept={vi.fn()} onDiscard={vi.fn()} onReload={vi.fn()} />);
    expect(screen.getByText('<img src=x onerror=alert(1)>', { exact: false })).toBeInTheDocument();
    expect(document.querySelector('img')).toBeNull();
    expect(document.querySelector('iframe')).toBeNull();
    expect(screen.getByText('Not saved')).toBeInTheDocument();
  });
});
