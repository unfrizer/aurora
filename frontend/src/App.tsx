import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError, createProject, deleteProject, listProjects, openProject, renameProject, saveEditor } from './api';
import { DEFAULT_MODEL } from './config';
import { blankEditor } from './editor';
import { t } from './i18n';
import type { EditorDocument, Language, ProjectDocument, ProjectMetadata } from './types';
import { parseEditor } from './types';
import { ExportDeploy } from './components/ExportDeploy';
import { Onboarding } from './components/Onboarding';
import { Projects } from './components/Projects';
import { Settings } from './components/Settings';
import { Workspace } from './components/Workspace';

type Screen = 'projects' | 'workspace' | 'settings' | 'export';

function message(error: unknown, language: Language): string {
  if (error instanceof ApiError) {
    if (error.status === 400) return t(language, 'error400');
    if (error.status === 404) return t(language, 'error404');
    if (error.status === 409) return t(language, 'error409');
    if (error.status === 503 || error.status === 502 || error.status === 504) return t(language, 'error503');
    return t(language, 'error500');
  }
  if (error instanceof TypeError) return t(language, 'networkError');
  return t(language, 'badResponse');
}

export default function App() {
  const [language, setLanguage] = useState<Language | null>(null);
  const [guide, setGuide] = useState(true);
  const [screen, setScreen] = useState<Screen>('projects');
  const [model, setModel] = useState(DEFAULT_MODEL);
  const [projects, setProjects] = useState<ProjectMetadata[]>([]);
  const [active, setActive] = useState<ProjectDocument | null>(null);
  const [editor, setEditor] = useState<EditorDocument | null>(null);
  const [editorError, setEditorError] = useState(false);
  const [busy, setBusy] = useState(false);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [error, setError] = useState('');
  const docRef = useRef<ProjectDocument | null>(null);
  const editorRef = useRef<EditorDocument | null>(null);
  const dirtyRef = useRef(false);
  const blockedRef = useRef(false);
  const revisionRef = useRef(0);
  const queueRef = useRef<Promise<void>>(Promise.resolve());
  const lang = language ?? 'en';
  const onError = useCallback((reason: unknown) => setError(message(reason, lang)), [lang]);

  useEffect(() => {
    if (!language) return;
    void listProjects().then(setProjects).catch(onError);
  }, [language, onError]);

  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (dirtyRef.current) { event.preventDefault(); event.returnValue = ''; }
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, []);

  function setDocument(document: ProjectDocument, loadedEditor: EditorDocument | null, bad = false) {
    docRef.current = document; editorRef.current = loadedEditor;
    setActive(document); setEditor(loadedEditor); setEditorError(bad);
    dirtyRef.current = false; blockedRef.current = false;
    setDirty(false); setError(''); revisionRef.current = 0;
  }

  async function refresh() { setProjects(await listProjects()); }

  async function open(id: string) {
    setBusy(true);
    try {
      await queueRef.current;
      const document = await openProject(id);
      let decoded: EditorDocument | null = null;
      let bad = false;
      if ('editor' in document.state) {
        try { decoded = parseEditor(document.state.editor); } catch { bad = true; }
      }
      setDocument(document, decoded, bad); setScreen('workspace');
    } catch (reason) { onError(reason); }
    finally { setBusy(false); }
  }

  async function create(name: string) {
    setBusy(true);
    try {
      const document = await createProject(name);
      setDocument(document, null); await refresh(); setScreen('workspace');
    } catch (reason) { onError(reason); }
    finally { setBusy(false); }
  }

  async function remove(id: string): Promise<boolean> {
    setBusy(true);
    try { await deleteProject(id); await refresh(); return true; }
    catch (reason) { onError(reason); return false; }
    finally { setBusy(false); }
  }

  async function startBlank() {
    const document = docRef.current;
    if (!document || !language || editorRef.current || editorError) return;
    setBusy(true);
    try {
      const initial = blankEditor(document.metadata.name, language);
      const saved = await saveEditor(document.metadata.project_id, initial, document.metadata.updated_at);
      setDocument(saved, parseEditor(saved.state.editor));
      await refresh();
    } catch (reason) { onError(reason); }
    finally { setBusy(false); }
  }

  async function commit(next: EditorDocument): Promise<boolean> {
    editorRef.current = next; setEditor(next); setError('');
    dirtyRef.current = true; setDirty(true);
    const revision = ++revisionRef.current;
    const work = queueRef.current.then(async () => {
      const base = docRef.current;
      if (blockedRef.current || !base) return false;
      setSaving(true);
      try {
        const saved = await saveEditor(base.metadata.project_id, next, base.metadata.updated_at);
        docRef.current = saved; setActive(saved);
        if (revision === revisionRef.current) { dirtyRef.current = false; setDirty(false); }
        return true;
      } catch (reason) {
        // A rejected 400 has no persistence effect; a corrected confirmed edit may
        // be sent. Other failures can leave the saved timestamp uncertain.
        blockedRef.current = !(reason instanceof ApiError && reason.status === 400);
        onError(reason);
        return false;
      } finally { setSaving(false); }
    });
    queueRef.current = work.then(() => undefined);
    return work;
  }

  async function flush(): Promise<string | null> {
    await queueRef.current;
    if (dirtyRef.current || blockedRef.current || !docRef.current || !editorRef.current) {
      setError(blockedRef.current ? t(lang, 'conflict') : t(lang, 'unsaved'));
      return null;
    }
    return docRef.current.metadata.updated_at;
  }

  async function reload() {
    const id = docRef.current?.metadata.project_id;
    if (!id) return;
    if (dirtyRef.current && !window.confirm(t(lang, 'reloadConfirm'))) return;
    await queueRef.current;
    await open(id);
  }

  async function rename(name: string): Promise<boolean> {
    if (!name.trim()) { setError(t(lang, 'error400')); return false; }
    const timestamp = await flush();
    if (!timestamp || !docRef.current) return false;
    try {
      const updated = await renameProject(docRef.current, name);
      docRef.current = updated; setActive(updated); await refresh(); return true;
    } catch (reason) { onError(reason); return false; }
  }

  async function navigate(next: Screen) {
    await queueRef.current;
    if (dirtyRef.current && !window.confirm(t(lang, 'leaveConfirm'))) return;
    if (next === 'export' && !(await flush())) return;
    if (next === 'projects') try { await refresh(); } catch (reason) { onError(reason); }
    setScreen(next);
  }

  return <div className="app-shell">
    <header className="topbar"><button className="brandmark" onClick={() => void navigate('projects')}>✦ <span>AURORA</span></button>
      <nav aria-label="Main navigation">
        <button className={screen === 'projects' ? 'active' : ''} onClick={() => void navigate('projects')}>{t(lang, 'projects')}</button>
        {active && <button className={screen === 'workspace' ? 'active' : ''} onClick={() => void navigate('workspace')}>{t(lang, 'workspace')}</button>}
        {active && editor && <button className={screen === 'export' ? 'active' : ''} onClick={() => void navigate('export')}>{t(lang, 'export')}</button>}
        <button className={screen === 'settings' ? 'active' : ''} onClick={() => void navigate('settings')}>{t(lang, 'settings')}</button>
      </nav>
      <button className="guide-link" onClick={() => setGuide(true)}>{t(lang, 'onboarding')}</button>
    </header>
    {error && <div className="error-banner" role="alert">{error}<button aria-label={t(lang, 'close')} onClick={() => setError('')}>×</button></div>}
    {screen === 'projects' && <Projects language={lang} projects={projects} busy={busy} onCreate={create} onOpen={open} onDelete={remove} />}
    {screen === 'workspace' && active && (editorError
      ? <main className="empty-workspace"><h1>{active.metadata.name}</h1><p role="alert">{t(lang, 'badEditor')}</p><button onClick={() => void reload()}>{t(lang, 'reload')}</button></main>
      : editor
        ? <Workspace language={lang} projectId={active.metadata.project_id} projectName={active.metadata.name} editor={editor}
            model={model} dirty={dirty} saving={saving} onCommit={commit} onFlush={flush} onRename={rename} onReload={reload} onError={onError} />
        : <main className="empty-workspace"><span className="eyebrow">NEW WORKSPACE</span><h1>{active.metadata.name}</h1>
            <p>{t(lang, 'noGeneration')}</p><button className="primary" disabled={busy} onClick={() => void startBlank()}>{t(lang, 'blank')}</button></main>)}
    {screen === 'settings' && <Settings language={lang} onLanguage={setLanguage} model={model} onModel={setModel} onError={onError} />}
    {screen === 'export' && active && editor && <ExportDeploy language={lang} projectId={active.metadata.project_id} ready={flush} onError={onError} />}
    {guide && <Onboarding language={language} onLanguage={setLanguage} onClose={() => setGuide(false)} />}
  </div>;
}
