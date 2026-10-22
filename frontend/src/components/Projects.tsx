import { useState } from 'react';
import { t } from '../i18n';
import { preparedSitePrompt } from '../prepared_site_prompt';
import { validDraftInputs } from '../types';
import type { Language, ProjectMetadata } from '../types';

interface Props {
  language: Language;
  projects: ProjectMetadata[];
  busy: boolean;
  model: string;
  onCreate: (name: string) => Promise<void>;
  onGenerate: (name: string, prompt: string) => Promise<void>;
  onImport: (name: string, file: File) => Promise<void>;
  onOpen: (id: string) => Promise<void>;
  onDelete: (id: string) => Promise<boolean>;
}

export function Projects({ language, projects, busy, model, onCreate, onGenerate, onImport, onOpen, onDelete }: Props) {
  const [name, setName] = useState('');
  const [prompt, setPrompt] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [pastedJson, setPastedJson] = useState('');
  const [deleting, setDeleting] = useState<ProjectMetadata | null>(null);
  const [confirmation, setConfirmation] = useState('');
  return <main className="projects-page">
    <div className="hero">
      <span className="eyebrow">PROJECTS / 01</span>
      <h1>{t(language, 'projects')}</h1>
      <p>{t(language, 'projectsIntro')}</p>
    </div>
    <div className="projects-grid">
      <form className="card new-project" onSubmit={(event) => {
        event.preventDefault();
        const trimmed = name.trim();
        if (trimmed) void onCreate(trimmed);
      }}>
        <span className="eyebrow">NEW PROJECT</span>
        <label>{t(language, 'projectName')}<input value={name} onChange={(event) => setName(event.target.value)} required /></label>
        <label>{t(language, 'businessPrompt')}<textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={5} /></label>
        <div className="actions"><button disabled={busy || !name.trim()}>{t(language, 'create')}</button>
          <button className="primary" type="button" disabled={busy || !validDraftInputs(name, prompt, model)}
            onClick={() => void onGenerate(name, prompt)}>{t(language, 'generateDraft')}</button></div>
        <small>{t(language, 'generationScope')}</small>
        <details>
          <summary>{t(language, 'importGuide')}</summary>
          <p>{t(language, 'importGuideNote')}</p>
          <label>{t(language, 'importGuidePrompt')}
            <textarea readOnly value={preparedSitePrompt(language)} rows={18}
              onFocus={(event) => event.currentTarget.select()} />
          </label>
        </details>
        <label>{t(language, 'importFile')}<input type="file" accept=".json,application/json"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)} /></label>
        <div className="actions"><button type="button" disabled={busy || !name.trim() || !file}
          onClick={() => { if (file) void onImport(name.trim(), file); }}>{t(language, 'importPrepared')}</button></div>
        <label>{t(language, 'importPasteLabel')}<textarea value={pastedJson}
          onChange={(event) => setPastedJson(event.target.value)} rows={6} /></label>
        <div className="actions"><button type="button" disabled={busy || !name.trim() || !pastedJson.trim()}
          onClick={() => void onImport(name.trim(), new File([pastedJson], 'pasted-site.json', { type: 'application/json' }))}>
          {t(language, 'importPasteAction')}</button></div>
        <small>{t(language, 'importPasteScope')}</small>
        <small>{t(language, 'importScope')}</small>
      </form>
      <section className="project-list" aria-label={t(language, 'projects')}>
        {projects.length === 0 && <p className="muted">{t(language, 'noProjects')}</p>}
        {projects.map((project) => <article className="card project-card" key={project.project_id}>
          <div><span className="eyebrow">AURORA PROJECT</span><h2>{project.name}</h2><small>{project.updated_at}</small></div>
          <div className="actions">
            <button onClick={() => void onOpen(project.project_id)} disabled={busy}>{t(language, 'open')}</button>
            <button className="danger-quiet" onClick={() => { setDeleting(project); setConfirmation(''); }} disabled={busy}>{t(language, 'delete')}</button>
          </div>
        </article>)}
      </section>
    </div>
    {deleting && <div className="overlay" role="dialog" aria-modal="true" aria-label={t(language, 'delete')}>
      <div className="dialog"><h2>{t(language, 'delete')}</h2><p>{t(language, 'typeName')}: <strong>{deleting.name}</strong></p>
        <input aria-label={t(language, 'typeName')} value={confirmation} onChange={(event) => setConfirmation(event.target.value)} />
        <div className="actions"><button onClick={() => setDeleting(null)}>{t(language, 'cancel')}</button>
          <button className="danger" disabled={busy || confirmation !== deleting.name} onClick={() => void onDelete(deleting.project_id).then((removed) => { if (removed) setDeleting(null); })}>{t(language, 'delete')}</button></div>
      </div>
    </div>}
  </main>;
}
