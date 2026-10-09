import { useState } from 'react';
import { t } from '../i18n';
import type { Language, ProjectMetadata } from '../types';

interface Props {
  language: Language;
  projects: ProjectMetadata[];
  busy: boolean;
  onCreate: (name: string) => Promise<void>;
  onOpen: (id: string) => Promise<void>;
  onDelete: (id: string) => Promise<boolean>;
}

export function Projects({ language, projects, busy, onCreate, onOpen, onDelete }: Props) {
  const [name, setName] = useState('');
  const [deleting, setDeleting] = useState<ProjectMetadata | null>(null);
  const [confirmation, setConfirmation] = useState('');
  return <main className="projects-page">
    <div className="hero">
      <span className="eyebrow">PROJECTS / 01</span>
      <h1>{t(language, 'projects')}</h1>
      <p>{t(language, 'noGeneration')}</p>
    </div>
    <div className="projects-grid">
      <form className="card new-project" onSubmit={(event) => {
        event.preventDefault();
        const trimmed = name.trim();
        if (trimmed) void onCreate(trimmed);
      }}>
        <span className="eyebrow">NEW PROJECT</span>
        <label>{t(language, 'projectName')}<input value={name} onChange={(event) => setName(event.target.value)} required maxLength={120} /></label>
        <button className="primary" disabled={busy || !name.trim()}>{t(language, 'create')}</button>
        <small>{t(language, 'blank')}</small>
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
