import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { ProjectGeneration } from '../src/components/ProjectGeneration';
import { GenerationErrorNotice } from '../src/components/GenerationErrorNotice';
import { TextAssist } from '../src/components/TextAssist';
import { blankEditor } from '../src/editor';
import { parseDraftResult, validDraftInputs, type DraftResult } from '../src/types';

const id = '00000000-0000-4000-8000-000000000001';
const source = '2026-10-12T12:00:00Z';
const generateText = vi.hoisted(() => vi.fn());
vi.mock('../src/api', async (original) => ({ ...(await original<typeof import('../src/api')>()), generateText }));

describe('P6 project draft validation', () => {
  it.each(['ru', 'en'] as const)('explains exhausted credits in %s without displaying provider text or retrying', (language) => {
    const onGenerate = vi.fn();
    render(<ProjectGeneration language={language} projectName="Studio" model="m" prompt="brief"
      candidate={null} failure={{ job_id: id, status: 'failed', source_updated_at: source, editor: null,
        failure: { category: 'rate_limited', retryable: false, message: 'PRIVATE_PROVIDER_BODY' } }}
      pending={false} accepting={false} conflict={false} onPrompt={vi.fn()}
      onGenerate={onGenerate} onAccept={vi.fn()} onDiscard={vi.fn()} onReload={vi.fn()} />);
    expect(screen.getByRole('alert')).toHaveTextContent(language === 'ru' ? 'API-кредитов' : 'API credits');
    expect(screen.queryByText('PRIVATE_PROVIDER_BODY')).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: language === 'ru' ? 'Баланс API OpenAI' : 'OpenAI API balance' }))
      .toHaveAttribute('href', 'https://platform.openai.com/settings/organization/billing/overview');
    expect(onGenerate).not.toHaveBeenCalled();
  });

  it.each(['authentication', 'remote', 'network', 'invalid_response', '__proto__'])
    ('uses localized guidance for %s without trusting provider output', (category) => {
      render(<GenerationErrorNotice language="ru" title="Ошибка" failure={{ category, retryable: false }} />);
      expect(screen.getByRole('alert').textContent!.length).toBeGreaterThan(30);
      expect(screen.queryByRole('link')).not.toBeInTheDocument();
    });

  it('shows quota guidance for selected-block text assistance without generic server errors', async () => {
    generateText.mockResolvedValueOnce({ job_id: id, status: 'failed', result: null,
      failure: { category: 'rate_limited', retryable: false, message: 'PRIVATE_PROVIDER_BODY' } });
    const onError = vi.fn();
    render(<TextAssist language="ru" section={blankEditor('Studio', 'ru').pages[0]!.sections[0]!}
      model="m" onAccept={vi.fn()} onError={onError} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Перепиши текст' } });
    fireEvent.click(screen.getByRole('button', { name: 'Создать вариант' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('API-кредитов');
    expect(onError).not.toHaveBeenCalled();
    expect(generateText).toHaveBeenCalledTimes(1);
    expect(screen.queryByText('PRIVATE_PROVIDER_BODY')).not.toBeInTheDocument();
  });
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
