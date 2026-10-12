import { t } from '../i18n';
import { validDraftInputs, type DraftResult, type Language } from '../types';

interface Props {
  language: Language;
  projectName: string;
  model: string;
  prompt: string;
  candidate: Extract<DraftResult, { status: 'completed' }> | null;
  failure: Extract<DraftResult, { status: 'failed' }> | null;
  pending: boolean;
  accepting: boolean;
  conflict: boolean;
  onPrompt: (value: string) => void;
  onGenerate: () => void;
  onAccept: () => void;
  onDiscard: () => void;
  onReload: () => void;
}

export function ProjectGeneration({ language, projectName, model, prompt, candidate, failure,
  pending, accepting, conflict, onPrompt, onGenerate, onAccept, onDiscard, onReload }: Props) {
  return <main className="generation-page">
    <span className="eyebrow">PROJECT DRAFT</span>
    <h1>{projectName}</h1>
    {pending ? <section className="card generation-status" role="status">
      <h2>{t(language, 'generationPending')}</h2><p>{t(language, 'generationUncertain')}</p>
    </section> : candidate ? <section className="generation-review" aria-label={t(language, 'draftReview')}>
      <div className="card generation-status"><span className="badge">{t(language, 'notSaved')}</span>
        <h2>{t(language, 'draftReview')}</h2><p>{t(language, 'draftReviewNote')}</p>
        {conflict && <p role="alert">{t(language, 'draftConflict')}</p>}
        <div className="actions"><button className="primary" disabled={accepting || conflict} onClick={onAccept}>{accepting ? t(language, 'saving') : t(language, 'acceptDraft')}</button>
          <button disabled={accepting} onClick={onDiscard}>{t(language, 'discardDraft')}</button>
          {conflict && <button onClick={onReload}>{t(language, 'reload')}</button>}</div>
      </div>
      <section className="card"><h2>{t(language, 'brand')}</h2>
        <p><strong>{candidate.editor.brand.name}</strong> — {candidate.editor.brand.tagline}</p>
        <p>{t(language, 'primary')}: {candidate.editor.brand.primary_color} · {t(language, 'secondary')}: {candidate.editor.brand.secondary_color} · {t(language, 'font')}: {candidate.editor.brand.font_family}</p>
      </section>
      {candidate.editor.pages.map((page) => <section className="card" key={page.id}>
        <span className="eyebrow">/{page.slug}</span><h2>{page.heading}</h2>
        <p>{t(language, 'title')}: {page.title}</p><p>{t(language, 'description')}: {page.meta_description}</p>
        {page.sections.map((section) => <article className="generation-section" key={section.id}>
          <h3>{section.heading}</h3><p>{section.body}</p>
        </article>)}
      </section>)}
    </section> : <section className="card generation-input">
      {failure && <p role="alert">{t(language, 'generationFailed')}: {failure.failure.category}</p>}
      <label>{t(language, 'businessPrompt')}<textarea value={prompt} onChange={(event) => onPrompt(event.target.value)} rows={6} /></label>
      <p className="muted">{t(language, 'generationScope')}</p>
      <button className="primary" disabled={!validDraftInputs(projectName, prompt, model)} onClick={onGenerate}>
        {failure ? t(language, 'tryAgain') : t(language, 'generateDraft')}
      </button>
    </section>}
  </main>;
}
