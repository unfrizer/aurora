import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { ApiError, createProject, deleteProject, generateProjectDraft, getPreferences, listProjects, openProject, renameProject, saveEditor, savePreferences } from './api';
import { DEFAULT_IMAGE_MODEL, DEFAULT_MODEL } from './config';
import { blankEditor } from './editor';
import { t } from './i18n';
import { offlineStarter, validOfflineBrief } from './offline_starter';
import { ImportValidationError, readPreparedEditor, sameEditor } from './project_import';
import type { DraftResult, EditorDocument, Language, PreferencesSnapshot, ProjectDocument, ProjectMetadata, UserPreferences } from './types';
import { parseEditor, validDraftInputs } from './types';
import { ExportDeploy } from './components/ExportDeploy';
import { GuidedImageCompletion } from './components/GuidedImageCompletion';
import { Onboarding } from './components/Onboarding';
import { Projects } from './components/Projects';
import { ProjectGeneration } from './components/ProjectGeneration';
import { Settings } from './components/Settings';
import { Workspace } from './components/Workspace';

type Screen = 'projects' | 'workspace' | 'settings' | 'export' | 'generation' | 'guided-images';

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
  const [onboardingConflict, setOnboardingConflict] = useState(false);
  const [preferences, setPreferences] = useState<PreferencesSnapshot | null>(null);
  const [preferencesLoading, setPreferencesLoading] = useState(true);
  const [preferencesBusy, setPreferencesBusy] = useState(false);
  const [screen, setScreen] = useState<Screen>('projects');
  const [model, setModel] = useState(DEFAULT_MODEL);
  const [imageModel, setImageModel] = useState(DEFAULT_IMAGE_MODEL);
  const [imageLocked, setImageLocked] = useState(false);
  const [projects, setProjects] = useState<ProjectMetadata[]>([]);
  const [active, setActive] = useState<ProjectDocument | null>(null);
  const [editor, setEditor] = useState<EditorDocument | null>(null);
  const [editorError, setEditorError] = useState(false);
  const [busy, setBusy] = useState(false);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [error, setError] = useState('');
  const [generationPrompt, setGenerationPrompt] = useState('');
  const [candidate, setCandidate] = useState<Extract<DraftResult, { status: 'completed' }> | null>(null);
  const [generationFailure, setGenerationFailure] = useState<Extract<DraftResult, { status: 'failed' }> | null>(null);
  const [generating, setGenerating] = useState(false);
  const [accepting, setAccepting] = useState(false);
  const [generationConflict, setGenerationConflict] = useState(false);
  const docRef = useRef<ProjectDocument | null>(null);
  const editorRef = useRef<EditorDocument | null>(null);
  const dirtyRef = useRef(false);
  const blockedRef = useRef(false);
  const imageLockRef = useRef(false);
  const preferencesRef = useRef<PreferencesSnapshot | null>(null);
  const preferencesBusyRef = useRef(false);
  const importingRef = useRef(false);
  const offlineStartingRef = useRef(false);
  const revisionRef = useRef(0);
  const queueRef = useRef<Promise<void>>(Promise.resolve());
  const lang = language ?? 'en';
  const onError = useCallback((reason: unknown) => setError(message(reason, lang)), [lang]);

  function acceptPreferences(snapshot: PreferencesSnapshot, firstLoad = false) {
    preferencesRef.current = snapshot; setPreferences(snapshot);
    setOnboardingConflict(false);
    setLanguage(snapshot.preferences.language);
    setModel(snapshot.preferences.general_model); setImageModel(snapshot.preferences.image_model);
    if (firstLoad) setGuide(!snapshot.preferences.onboarding_completed || snapshot.preferences.language === null);
    setError('');
  }

  async function reloadPreferences(firstLoad = false): Promise<PreferencesSnapshot | null> {
    if (firstLoad) setPreferencesLoading(true);
    try {
      const snapshot = await getPreferences();
      acceptPreferences(snapshot, firstLoad);
      return snapshot;
    } catch (reason) {
      onError(reason);
      return null;
    } finally { if (firstLoad) setPreferencesLoading(false); }
  }

  useEffect(() => { void reloadPreferences(true); }, []);

  async function changePreferences(next: UserPreferences): Promise<'ok' | 'conflict' | 'error'> {
    const current = preferencesRef.current;
    if (!current || preferencesBusyRef.current) return 'error';
    preferencesBusyRef.current = true; setPreferencesBusy(true);
    try {
      const saved = await savePreferences(next, current.revision);
      acceptPreferences({ ...saved, projects_directory: current.projects_directory });
      return 'ok';
    } catch (reason) {
      onError(reason);
      return reason instanceof ApiError && reason.status === 409 ? 'conflict' : 'error';
    } finally { preferencesBusyRef.current = false; setPreferencesBusy(false); }
  }

  async function chooseLanguage(value: Language) {
    const current = preferencesRef.current;
    if (current && await changePreferences({ ...current.preferences, language: value }) === 'conflict') {
      setOnboardingConflict(true);
    }
  }

  async function closeGuide() {
    const current = preferencesRef.current;
    if (current) {
      const outcome = await changePreferences({ ...current.preferences, onboarding_completed: true });
      if (outcome === 'ok') setGuide(false);
      if (outcome === 'conflict') setOnboardingConflict(true);
    }
  }

  async function reloadOnboarding() {
    if (!window.confirm(t(lang, 'discardSettingsConfirm'))) return;
    await reloadPreferences(true);
  }

  async function saveSettings(value: Language, generalModel: string, nextImageModel: string) {
    const current = preferencesRef.current;
    if (!current) return 'error' as const;
    return changePreferences({ ...current.preferences, language: value,
      general_model: generalModel, image_model: nextImageModel });
  }

  useEffect(() => {
    if (!language) return;
    void listProjects().then(setProjects).catch(onError);
  }, [language, onError]);

  useLayoutEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (dirtyRef.current || generating || accepting || candidate) { event.preventDefault(); event.returnValue = ''; }
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [generating, accepting, candidate]);

  function setDocument(document: ProjectDocument, loadedEditor: EditorDocument | null, bad = false) {
    docRef.current = document; editorRef.current = loadedEditor;
    setActive(document); setEditor(loadedEditor); setEditorError(bad);
    dirtyRef.current = false; blockedRef.current = false;
    setDirty(false); setError(''); revisionRef.current = 0;
    setCandidate(null); setGenerationFailure(null); setGenerationConflict(false); setGenerationPrompt('');
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

  async function createWithBrief(name: string, brief: string) {
    if (offlineStartingRef.current || busy) return;
    if (!language || !validOfflineBrief(name, brief)) { setError(t(lang, 'error400')); return; }
    if (!window.confirm(t(lang, 'offlinePublicConfirm'))) return;
    offlineStartingRef.current = true; setBusy(true); setError('');
    let createAttempted = false;
    let created = false;
    try {
      const editor = offlineStarter(name, language, brief);
      createAttempted = true;
      const document = await createProject(name.trim());
      created = true;
      const saved = await saveEditor(document.metadata.project_id, editor, document.metadata.updated_at);
      const loaded = parseEditor(saved.state.editor);
      if (saved.metadata.project_id !== document.metadata.project_id || !sameEditor(editor, loaded)) {
        throw new Error('Saved offline starter does not match');
      }
      setDocument(saved, loaded); setScreen('workspace');
      try { await refresh(); } catch (reason) { onError(reason); }
    } catch (reason) {
      if (created) setError(t(lang, 'offlineSaveUncertain'));
      else if (createAttempted) setError(t(lang, 'offlineCreateUncertain'));
      else onError(reason);
      if (createAttempted) try { await refresh(); } catch { /* Preserve the primary recovery message. */ }
    } finally { offlineStartingRef.current = false; setBusy(false); }
  }

  async function importPrepared(name: string, file: File) {
    if (importingRef.current || busy) return;
    importingRef.current = true; setBusy(true); setError('');
    let createAttempted = false;
    let created = false;
    try {
      const imported = await readPreparedEditor(file);
      createAttempted = true;
      const document = await createProject(name);
      created = true;
      const saved = await saveEditor(document.metadata.project_id, imported, document.metadata.updated_at);
      const loaded = parseEditor(saved.state.editor);
      if (saved.metadata.project_id !== document.metadata.project_id ||
          !sameEditor(imported, loaded)) {
        throw new Error('Saved import does not match');
      }
      setDocument(saved, loaded); setScreen('workspace');
      try { await refresh(); } catch (reason) { onError(reason); }
    } catch (reason) {
      if (reason instanceof ImportValidationError) {
        const labels = { size: 'importSize', encoding: 'importEncoding', json: 'importJson',
          schema: 'importSchema', assets: 'importAssets', read: 'importRead' } as const;
        setError(t(lang, labels[reason.reason]));
      } else if (created) {
        setError(t(lang, 'importSaveFailed'));
        try { await refresh(); } catch { /* Preserve the import failure as the primary message. */ }
      } else if (createAttempted) {
        setError(t(lang, 'importCreateFailed'));
        try { await refresh(); } catch { /* Preserve the import failure as the primary message. */ }
      } else onError(reason);
    } finally { importingRef.current = false; setBusy(false); }
  }

  async function runDraft(document: ProjectDocument, prompt: string) {
    if (!language || !validDraftInputs(document.metadata.name, prompt, model)) return;
    setGenerationPrompt(prompt); setCandidate(null); setGenerationFailure(null);
    setGenerationConflict(false); setError(''); setScreen('generation'); setGenerating(true);
    try {
      const result = await generateProjectDraft(
        document.metadata.project_id, prompt, language, model, document.metadata.updated_at,
      );
      if (result.status === 'completed') setCandidate(result);
      else setGenerationFailure(result);
    } catch (reason) { onError(reason); }
    finally { setGenerating(false); }
  }

  async function generateNew(name: string, prompt: string) {
    if (!language || !validDraftInputs(name, prompt, model)) { setError(t(lang, 'error400')); return; }
    if (!window.confirm(t(lang, 'generationConfirm'))) return;
    setBusy(true);
    try {
      const document = await createProject(name);
      setDocument(document, null); setScreen('generation');
      try { await refresh(); } catch (reason) { onError(reason); }
      await runDraft(document, prompt);
    } catch (reason) { onError(reason); }
    finally { setBusy(false); }
  }

  async function generateExisting() {
    const document = docRef.current;
    if (!document || editorRef.current || editorError ||
        !validDraftInputs(document.metadata.name, generationPrompt, model)) return;
    if (!window.confirm(t(lang, 'generationConfirm'))) return;
    await runDraft(document, generationPrompt);
  }

  async function acceptDraft() {
    const draft = candidate;
    const document = docRef.current;
    if (!draft || !document || accepting || generationConflict) return;
    setAccepting(true);
    try {
      const saved = await saveEditor(document.metadata.project_id, draft.editor, draft.source_updated_at);
      if (saved.metadata.project_id !== document.metadata.project_id) throw new Error('Invalid saved project');
      const loaded = parseEditor(saved.state.editor);
      setDocument(saved, loaded); setScreen('guided-images'); await refresh();
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 409) setGenerationConflict(true);
      onError(reason);
    } finally { setAccepting(false); }
  }

  function discardDraft() {
    if (candidate && !window.confirm(t(lang, 'discardConfirm'))) return;
    setCandidate(null); setGenerationFailure(null); setGenerationConflict(false);
    setGenerationPrompt(''); setScreen('workspace');
  }

  async function reloadGeneration() {
    const id = docRef.current?.metadata.project_id;
    if (!id || (candidate && !window.confirm(t(lang, 'discardConfirm')))) return;
    setCandidate(null); setGenerationFailure(null); setGenerationConflict(false);
    await open(id);
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

  async function imageSnapshot(): Promise<{ editor: EditorDocument; updatedAt: string } | null> {
    const updatedAt = await flush();
    return updatedAt && editorRef.current ? { editor: editorRef.current, updatedAt } : null;
  }

  function imageDocument(document: ProjectDocument, loadedEditor: EditorDocument) {
    setDocument(document, loadedEditor);
    void refresh().catch(onError);
  }

  function imageLock(locked: boolean) {
    imageLockRef.current = locked;
    setImageLocked(locked);
  }

  async function startGuidedImages() {
    if (imageLockRef.current || !editorRef.current || !(await flush())) return;
    setScreen('guided-images');
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
    if (busy || generating || accepting || imageLockRef.current) return;
    await queueRef.current;
    if (dirtyRef.current && !window.confirm(t(lang, 'leaveConfirm'))) return;
    if (candidate && next !== 'generation') {
      if (!window.confirm(t(lang, 'discardConfirm'))) return;
      setCandidate(null); setGenerationFailure(null); setGenerationConflict(false);
      setGenerationPrompt('');
    }
    if (next === 'export' && !(await flush())) return;
    if (next === 'projects') try { await refresh(); } catch (reason) { onError(reason); }
    setScreen(next);
  }

  if (preferencesLoading) return <main className="settings-page" role="status">{t(lang, 'loadingPreferences')}</main>;
  if (!preferences) return <main className="settings-page"><h1>AURORA</h1>
    <p role="alert">{t(lang, 'preferencesUnavailable')}</p>
    <button onClick={() => void reloadPreferences(true)}>{t(lang, 'tryAgain')}</button></main>;

  return <div className="app-shell">
    <header className="topbar"><button className="brandmark" disabled={busy || generating || accepting || imageLocked} onClick={() => void navigate('projects')}>✦ <span>AURORA</span></button>
      <nav aria-label="Main navigation">
        <button disabled={busy || generating || accepting || imageLocked} className={screen === 'projects' ? 'active' : ''} onClick={() => void navigate('projects')}>{t(lang, 'projects')}</button>
        {active && <button disabled={busy || generating || accepting || imageLocked} className={screen === 'workspace' ? 'active' : ''} onClick={() => void navigate('workspace')}>{t(lang, 'workspace')}</button>}
        {active && editor && <button disabled={busy || generating || accepting || imageLocked} className={screen === 'export' ? 'active' : ''} onClick={() => void navigate('export')}>{t(lang, 'export')}</button>}
        <button disabled={busy || generating || accepting || imageLocked} className={screen === 'settings' ? 'active' : ''} onClick={() => void navigate('settings')}>{t(lang, 'settings')}</button>
      </nav>
      <button className="guide-link" disabled={busy || generating || accepting || imageLocked} onClick={() => setGuide(true)}>{t(lang, 'onboarding')}</button>
    </header>
    {error && <div className="error-banner" role="alert">{error}<button aria-label={t(lang, 'close')} onClick={() => setError('')}>×</button></div>}
    {screen === 'projects' && <Projects language={lang} projects={projects} busy={busy} model={model} onCreate={create} onOffline={createWithBrief} onGenerate={generateNew} onImport={importPrepared} onOpen={open} onDelete={remove} />}
    {screen === 'generation' && active && <ProjectGeneration language={lang} projectName={active.metadata.name}
      model={model} prompt={generationPrompt} candidate={candidate} failure={generationFailure}
      pending={generating} accepting={accepting} conflict={generationConflict}
      onPrompt={setGenerationPrompt} onGenerate={() => void generateExisting()}
      onAccept={() => void acceptDraft()} onDiscard={discardDraft} onReload={() => void reloadGeneration()} />}
    {screen === 'workspace' && active && (editorError
      ? <main className="empty-workspace"><h1>{active.metadata.name}</h1><p role="alert">{t(lang, 'badEditor')}</p><button onClick={() => void reload()}>{t(lang, 'reload')}</button></main>
      : editor
        ? <Workspace language={lang} projectId={active.metadata.project_id} projectName={active.metadata.name} editor={editor}
            model={model} imageModel={imageModel} dirty={dirty} saving={saving} onCommit={commit} onFlush={flush}
            onImageSnapshot={imageSnapshot} onImageDocument={imageDocument} onImageLock={imageLock}
            onRename={rename} onReload={reload} onGuidedImages={startGuidedImages} onError={onError} />
        : <main className="empty-workspace"><span className="eyebrow">NEW WORKSPACE</span><h1>{active.metadata.name}</h1>
            <p>{t(lang, 'noGeneration')}</p><div className="actions"><button className="primary" disabled={busy} onClick={() => { setGenerationPrompt(''); setScreen('generation'); }}>{t(lang, 'generateDraft')}</button>
              <button disabled={busy} onClick={() => void startBlank()}>{t(lang, 'blank')}</button></div></main>)}
    {screen === 'settings' && <Settings language={lang} model={model} imageModel={imageModel}
      projectsDirectory={preferences.projects_directory} busy={preferencesBusy} onSave={saveSettings}
      onReload={() => reloadPreferences()} onError={onError} />}
    {screen === 'guided-images' && active && editor && <GuidedImageCompletion language={lang}
      projectId={active.metadata.project_id} editor={editor} model={imageModel}
      onSnapshot={imageSnapshot} onDocument={imageDocument} onLock={imageLock}
      onError={onError} onExit={() => setScreen('workspace')} />}
    {screen === 'export' && active && editor && <ExportDeploy language={lang} projectId={active.metadata.project_id} ready={flush} onError={onError} />}
    {guide && <Onboarding language={language} busy={preferencesBusy} conflict={onboardingConflict}
      onLanguage={(value) => void chooseLanguage(value)} onClose={() => void closeGuide()}
      onReload={() => void reloadOnboarding()} />}
  </div>;
}
