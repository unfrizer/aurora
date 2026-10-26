import { useRef, useState } from 'react';
import { t } from '../i18n';
import { preparedSitePrompt, preparedSitePromptWithBrief } from '../prepared_site_prompt';
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

function validExternalBrief(value: string): boolean {
  try {
    encodeURIComponent(value);
    return !!value.trim() && new TextEncoder().encode(value).length <= 8 * 1024;
  } catch { return false; }
}

export function Projects({ language, projects, busy, model, onCreate, onGenerate, onImport, onOpen, onDelete }: Props) {
  const [name, setName] = useState('');
  const [prompt, setPrompt] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const filePicker = useRef<HTMLInputElement>(null);
  const [fileDragging, setFileDragging] = useState(false);
  const [fileDropError, setFileDropError] = useState('');
  const [pastedJson, setPastedJson] = useState('');
  const [externalBrief, setExternalBrief] = useState('');
  const [guideCopy, setGuideCopy] = useState<'idle' | 'copied' | 'brief-copied' | 'failed'>('idle');
  const guideCopyRevision = useRef(0);
  const [deleting, setDeleting] = useState<ProjectMetadata | null>(null);
  const [confirmation, setConfirmation] = useState('');
  const [projectSearch, setProjectSearch] = useState('');
  const projectSearchKey = projectSearch.trim().toLowerCase();
  const visibleProjects = projectSearchKey
    ? projects.filter((project) => project.name.toLowerCase().includes(projectSearchKey))
    : projects;
  async function copyGuide(value: string, outcome: 'copied' | 'brief-copied') {
    const revision = guideCopyRevision.current;
    try {
      await navigator.clipboard.writeText(value);
      if (guideCopyRevision.current === revision) setGuideCopy(outcome);
    } catch {
      if (guideCopyRevision.current === revision) setGuideCopy('failed');
    }
  }
  function changeExternalBrief(value: string) {
    guideCopyRevision.current += 1;
    setExternalBrief(value);
    setGuideCopy('idle');
  }
  return <main className="projects-page">
    <div className="hero">
      <span className="eyebrow">PROJECTS / 01</span>
      <h1>{t(language, 'projects')}</h1>
      <p>{t(language, 'projectsIntro')}</p>
    </div>
    <div className="projects-grid">
      <div className="card new-project">
        <span className="eyebrow">NEW PROJECT</span>
        <label>{t(language, 'projectName')}<input value={name} onChange={(event) => setName(event.target.value)} required /></label>
        <section className="project-path" aria-labelledby="project-ai-path">
          <div className="project-path-head"><h2 id="project-ai-path">{t(language, 'projectAiPath')}</h2>
            <span className="badge">{t(language, 'projectAiBadge')}</span></div>
          <p>{t(language, 'projectAiPathNote')}</p>
          <label>{t(language, 'businessPrompt')}<textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={5} /></label>
          <div className="actions"><button className="primary" type="button"
            disabled={busy || !validDraftInputs(name, prompt, model)}
            onClick={() => void onGenerate(name, prompt)}>{t(language, 'generateDraft')}</button></div>
          <small>{t(language, 'generationScope')}</small>
        </section>
        <section className="project-path" aria-labelledby="project-blank-path">
          <div className="project-path-head"><h2 id="project-blank-path">{t(language, 'projectBlankPath')}</h2>
            <span className="badge good">{t(language, 'projectNoKeyBadge')}</span></div>
          <p>{t(language, 'projectBlankPathNote')}</p>
          <div className="actions"><button type="button" disabled={busy || !name.trim()}
            onClick={() => { const trimmed = name.trim(); if (trimmed) void onCreate(trimmed); }}>
            {t(language, 'create')}</button></div>
        </section>
        <section className="project-path" aria-labelledby="project-import-path">
          <div className="project-path-head"><h2 id="project-import-path">{t(language, 'projectImportPath')}</h2>
            <span className="badge good">{t(language, 'projectNoKeyBadge')}</span></div>
          <p>{t(language, 'projectImportPathNote')}</p>
          <details>
            <summary>{t(language, 'importGuide')}</summary>
            <p>{t(language, 'importGuideNote')}</p>
            <label>{t(language, 'importGuidePrompt')}
              <textarea readOnly value={preparedSitePrompt(language)} rows={18}
                onFocus={(event) => event.currentTarget.select()} />
            </label>
            <div className="actions"><button type="button"
              onClick={() => void copyGuide(preparedSitePrompt(language), 'copied')}>
              {t(language, 'importGuideCopy')}</button></div>
            <label>{t(language, 'importGuideBrief')}<textarea value={externalBrief} rows={6}
              onChange={(event) => changeExternalBrief(event.target.value)} /></label>
            <small>{t(language, 'importGuideBriefNote')}</small>
            <div className="actions"><button type="button" disabled={!validExternalBrief(externalBrief)}
              onClick={() => void copyGuide(preparedSitePromptWithBrief(language, externalBrief), 'brief-copied')}>
              {t(language, 'importGuideBriefCopy')}</button>
              {externalBrief.length > 0 && <button type="button" disabled={busy}
                onClick={() => changeExternalBrief('')}>{t(language, 'importGuideBriefClear')}</button>}</div>
            {guideCopy !== 'idle' && <p role="status">{t(language,
              guideCopy === 'copied' ? 'importGuideCopied'
                : guideCopy === 'brief-copied' ? 'importGuideBriefCopied' : 'importGuideCopyFailed')}</p>}
          </details>
          <div className={`import-drop-zone${fileDragging ? ' dragging' : ''}`} role="region"
            aria-label={t(language, 'importDropZone')}
            onDragEnter={(event) => { event.preventDefault(); setFileDragging(true); }}
            onDragOver={(event) => { event.preventDefault(); event.dataTransfer.dropEffect = 'copy'; }}
            onDragLeave={(event) => { event.preventDefault(); setFileDragging(false); }}
            onDrop={(event) => {
              event.preventDefault(); setFileDragging(false);
              const selected = Array.from(event.dataTransfer.files);
              if (selected.length !== 1) { setFileDropError(t(language, 'importDropInvalid')); return; }
              if (filePicker.current) filePicker.current.value = '';
              setFile(selected[0] ?? null); setFileDropError('');
            }}>
            <p>{t(language, 'importDropNote')}</p>
            <label>{t(language, 'importFile')}<input ref={filePicker} type="file" accept=".json,application/json"
              onChange={(event) => { setFile(event.target.files?.[0] ?? null); setFileDropError(''); }} /></label>
            {file && <small aria-live="polite">{t(language, 'importDropSelected')} {file.name}</small>}
            {file && <div className="actions"><button type="button" disabled={busy} onClick={() => {
              setFile(null); setFileDropError('');
              if (filePicker.current) filePicker.current.value = '';
            }}>{t(language, 'importClearSelected')}</button></div>}
            {fileDropError && <p role="alert">{fileDropError}</p>}
          </div>
          <div className="actions"><button type="button" disabled={busy || !name.trim() || !file}
            onClick={() => { if (file) void onImport(name.trim(), file); }}>{t(language, 'importPrepared')}</button></div>
          <label>{t(language, 'importPasteLabel')}<textarea value={pastedJson}
            onChange={(event) => setPastedJson(event.target.value)} rows={6} /></label>
          <div className="actions"><button type="button" disabled={busy || !name.trim() || !pastedJson.trim()}
            onClick={() => void onImport(name.trim(), new File([pastedJson], 'pasted-site.json', { type: 'application/json' }))}>
            {t(language, 'importPasteAction')}</button>
            {pastedJson.length > 0 && <button type="button" disabled={busy} onClick={() => setPastedJson('')}>
              {t(language, 'importClearPasted')}</button>}</div>
          <small>{t(language, 'importPasteScope')}</small>
          <small>{t(language, 'importScope')}</small>
        </section>
      </div>
      <section className="project-list" aria-label={t(language, 'projects')}>
        {projects.length > 0 && <>
          <label>{t(language, 'projectSearch')}
            <input type="search" maxLength={128} value={projectSearch}
              onChange={(event) => setProjectSearch(event.target.value)} />
          </label>
          {projectSearch.length > 0 && <button type="button" onClick={() => setProjectSearch('')}>
            {t(language, 'clearProjectSearch')}
          </button>}
        </>}
        {projects.length === 0 && <p className="muted">{t(language, 'noProjects')}</p>}
        {projects.length > 0 && visibleProjects.length === 0
          && <p className="muted" aria-live="polite">{t(language, 'noProjectMatches')}</p>}
        {visibleProjects.map((project) => {
          const updated = new Date(project.updated_at);
          const validUpdated = Number.isFinite(updated.getTime());
          return <article className="card project-card" key={project.project_id}>
            <div><span className="eyebrow">AURORA PROJECT</span><h2>{project.name}</h2>
              <small>{t(language, 'lastUpdated')} {validUpdated
                ? <time dateTime={project.updated_at}>{new Intl.DateTimeFormat(language === 'ru' ? 'ru-RU' : 'en-US',
                  { dateStyle: 'medium', timeStyle: 'short' }).format(updated)}</time>
                : t(language, 'unknownUpdateTime')}</small></div>
            <div className="actions">
              <button onClick={() => void onOpen(project.project_id)} disabled={busy}>{t(language, 'open')}</button>
              <button className="danger-quiet" onClick={() => { setDeleting(project); setConfirmation(''); }} disabled={busy}>{t(language, 'delete')}</button>
            </div>
          </article>;
        })}
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
