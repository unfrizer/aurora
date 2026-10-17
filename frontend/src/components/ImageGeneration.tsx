import { useLayoutEffect, useRef, useState } from 'react';
import { ApiError, generateImage, openProject, rasterUrl, saveEditor } from '../api';
import { t } from '../i18n';
import type { EditorDocument, ImageResult, Language, ProjectDocument } from '../types';
import { parseEditor, validImageInputs } from '../types';

export type ImageTarget = { kind: 'logo' } | { kind: 'section'; pageId: string; sectionId: string };
export interface ImageSnapshot { editor: EditorDocument; updatedAt: string }

interface Props {
  language: Language;
  projectId: string;
  target: ImageTarget;
  targetLabel: string;
  model: string;
  onSnapshot: () => Promise<ImageSnapshot | null>;
  onDocument: (document: ProjectDocument, editor: EditorDocument) => void;
  onError: (error: unknown) => void;
  onClose: () => void;
  initialPrompt?: string;
  allowedTargets?: readonly ImageTarget[];
  requireEmptyTarget?: boolean;
  guided?: boolean;
  onAttached?: (target: ImageTarget) => void;
}

type Phase = 'form' | 'preparing' | 'pending' | 'review' | 'failed' | 'uncertain' | 'conflict' | 'reselect' | 'saving';
type Completed = Extract<ImageResult, { status: 'completed' }>;
type Failed = Extract<ImageResult, { status: 'failed' }>;

function sameTarget(left: ImageTarget, right: ImageTarget): boolean {
  return left.kind === right.kind && (left.kind === 'logo' ||
    (right.kind === 'section' && left.pageId === right.pageId && left.sectionId === right.sectionId));
}

function emptyTarget(editor: EditorDocument, target: ImageTarget): boolean {
  if (target.kind === 'logo') return editor.brand.logo_path === null;
  return editor.pages.find((page) => page.id === target.pageId)?.sections
    .find((section) => section.id === target.sectionId)?.image_path === null;
}

function targetOptions(editor: EditorDocument, language: Language, allowedTargets?: readonly ImageTarget[],
  requireEmptyTarget = false): { key: string; label: string; target: ImageTarget }[] {
  const all = [{ key: 'logo', label: t(language, 'imageLogoTarget'), target: { kind: 'logo' } as ImageTarget },
    ...editor.pages.flatMap((page) => page.sections.map((section) => ({
      key: `${page.id}/${section.id}`, label: `${page.title} / ${section.heading}`,
      target: { kind: 'section' as const, pageId: page.id, sectionId: section.id } as ImageTarget,
    })))];
  return all.filter(({ target }) => (!allowedTargets || allowedTargets.some((allowed) => sameTarget(allowed, target))) &&
    (!requireEmptyTarget || emptyTarget(editor, target)));
}

function withImage(editor: EditorDocument, target: ImageTarget, path: string, alt: string): EditorDocument | null {
  if (target.kind === 'logo') return { ...editor, brand: { ...editor.brand, logo_path: path } };
  const page = editor.pages.find((item) => item.id === target.pageId);
  if (!page || !page.sections.some((item) => item.id === target.sectionId)) return null;
  return { ...editor, pages: editor.pages.map((item) => item.id === target.pageId ? {
    ...item, sections: item.sections.map((section) => section.id === target.sectionId
      ? { ...section, image_path: path, image_alt: alt } : section),
  } : item) };
}

function hasTarget(editor: EditorDocument, target: ImageTarget): boolean {
  return target.kind === 'logo' || editor.pages.some((page) => page.id === target.pageId &&
    page.sections.some((section) => section.id === target.sectionId));
}

export function ImageGeneration({ language, projectId, target, targetLabel, model, onSnapshot, onDocument, onError,
  onClose, initialPrompt = '', allowedTargets, requireEmptyTarget = false, guided = false, onAttached }: Props) {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [alt, setAlt] = useState('');
  const [phase, setPhase] = useState<Phase>('form');
  const [snapshot, setSnapshot] = useState<ImageSnapshot | null>(null);
  const [candidate, setCandidate] = useState<Completed | null>(null);
  const [failure, setFailure] = useState<Failed | null>(null);
  const [pickedKey, setPickedKey] = useState('');
  const inFlight = useRef(false);
  const options = snapshot ? targetOptions(snapshot.editor, language, allowedTargets, requireEmptyTarget) : [];
  const chosen = phase === 'reselect' || pickedKey ? options.find((item) => item.key === pickedKey)?.target : target;
  const needsAlt = chosen?.kind === 'section';
  const risky = phase === 'pending' || phase === 'review' || phase === 'conflict' || phase === 'reselect' || phase === 'saving';

  useLayoutEffect(() => {
    if (!risky) return;
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ''; };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [risky]);

  async function generate() {
    if (inFlight.current || !validImageInputs(prompt, model) || (target.kind === 'section' && !alt.trim()) ||
        !window.confirm(t(language, guided ? 'guidedImageConfirm' : 'imageConfirm'))) return;
    inFlight.current = true;
    setPhase('preparing'); setFailure(null);
    let sent = false;
    try {
      const saved = await onSnapshot();
      if (!saved) { setPhase('form'); return; }
      if (!hasTarget(saved.editor, target) || (requireEmptyTarget && !emptyTarget(saved.editor, target))) {
        onError(new Error('Selected image target is unavailable')); setPhase('form'); return;
      }
      setSnapshot(saved); setPhase('pending');
      sent = true;
      const result = await generateImage(projectId, prompt, model, saved.updatedAt);
      if (result.status === 'completed') { setCandidate(result); setPhase('review'); }
      else { setFailure(result); setPhase('failed'); }
    } catch (error) { onError(error); setPhase(sent ? 'uncertain' : 'form'); }
    finally { inFlight.current = false; }
  }

  async function attach() {
    if (inFlight.current || !snapshot || !candidate || !chosen ||
        (phase !== 'review' && phase !== 'reselect')) return;
    if (needsAlt && !alt.trim()) { onError(new Error('Image alt text is required')); return; }
    if (requireEmptyTarget && !emptyTarget(snapshot.editor, chosen)) { setPhase('conflict'); return; }
    if (phase === 'reselect' && !window.confirm(t(language, 'imageReloadConfirm'))) return;
    const next = withImage(snapshot.editor, chosen, candidate.asset_path, alt);
    if (!next) { onError(new Error('Selected image target is unavailable')); return; }
    inFlight.current = true; setPhase('saving');
    try {
      const current = await onSnapshot();
      if (!current || current.updatedAt !== snapshot.updatedAt ||
          JSON.stringify(current.editor) !== JSON.stringify(snapshot.editor)) {
        setPhase('conflict'); return;
      }
      const saved = await saveEditor(projectId, next, snapshot.updatedAt);
      if (saved.metadata.project_id !== projectId) throw new Error('Invalid saved project');
      const decoded = parseEditor(saved.state.editor);
      if (!hasTarget(decoded, chosen)) throw new Error('Invalid saved image');
      const verified = chosen.kind === 'logo' ? decoded.brand.logo_path === candidate.asset_path :
        decoded.pages.find((page) => page.id === chosen.pageId)?.sections.find((section) => section.id === chosen.sectionId)?.image_path === candidate.asset_path;
      if (!verified) throw new Error('Invalid saved image');
      onDocument(saved, decoded); onAttached?.(chosen); onClose();
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) setPhase('conflict');
      else { onError(error); setPhase(phase === 'reselect' ? 'reselect' : 'review'); }
    } finally { inFlight.current = false; }
  }

  async function reloadForChoice() {
    if (inFlight.current || !candidate) return;
    inFlight.current = true;
    try {
      const document = await openProject(projectId);
      if (document.metadata.project_id !== projectId) throw new Error('Invalid project response');
      const editor = parseEditor(document.state.editor);
      onDocument(document, editor);
      setSnapshot({ editor, updatedAt: document.metadata.updated_at });
      setPickedKey(''); setAlt(''); setPhase('reselect');
    } catch (error) { onError(error); }
    finally { inFlight.current = false; }
  }

  function close() {
    if (inFlight.current || phase === 'preparing' || phase === 'pending' || phase === 'saving') return;
    if (candidate && !window.confirm(t(language, 'discardImageConfirm'))) return;
    onClose();
  }

  return <div className="overlay"><section className="dialog image-dialog" role="dialog" aria-modal="true" aria-label={t(language, 'generateImage')}>
    <h2>{t(language, 'generateImage')}</h2>
    {phase === 'form' && <>
      <p>{targetLabel}</p>
      <label>{t(language, 'imagePrompt')}<textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} /></label>
      {target.kind === 'section' && <label>{t(language, 'imageAltRequired')}<input value={alt} onChange={(event) => setAlt(event.target.value)} /></label>}
      <div className="actions"><button onClick={close}>{t(language, 'cancel')}</button>
        <button className="primary" disabled={!validImageInputs(prompt, model) || (target.kind === 'section' && !alt.trim())}
          onClick={() => void generate()}>{t(language, 'generateImage')}</button></div>
    </>}
    {phase === 'preparing' && <p role="status">{t(language, 'saving')}</p>}
    {phase === 'pending' && <><p role="status">{t(language, 'imagePending')}</p><p>{t(language, 'generationUncertain')}</p></>}
    {phase === 'failed' && <><p role="alert">{t(language, 'imageFailed')}: {failure?.failure.message}</p>
      <div className="actions"><button onClick={close}>{t(language, 'close')}</button><button onClick={() => setPhase('form')}>{t(language, 'tryAgain')}</button></div></>}
    {phase === 'uncertain' && <><p role="alert">{t(language, 'imageUncertain')}</p>
      <div className="actions"><button onClick={close}>{t(language, 'close')}</button><button onClick={() => setPhase('form')}>{t(language, 'tryAgain')}</button></div></>}
    {candidate && (phase === 'review' || phase === 'conflict' || phase === 'reselect' || phase === 'saving') && <>
      <strong>{t(language, 'imageStored')}</strong>
      <img className="image-candidate" src={rasterUrl(projectId, candidate.asset_path)} alt={alt || t(language, 'imageStored')} />
      <p>{t(language, 'imageTarget')}: {phase === 'reselect' || pickedKey
        ? options.find((item) => item.key === pickedKey)?.label ?? '—' : targetLabel}</p>
      {needsAlt && <p>{t(language, 'imageAlt')}: {alt}</p>}
      <p className="image-prompt-review">{prompt}</p><p>{t(language, 'imageStoredNote')}</p>
      {phase === 'conflict' && <p role="alert">{t(language, 'imageConflict')}</p>}
      {phase === 'reselect' && <label>{t(language, 'imageTarget')}<select value={pickedKey} onChange={(event) => setPickedKey(event.target.value)}>
        <option value="">—</option>{options.map((item) => <option key={item.key} value={item.key}>{item.label}</option>)}
      </select></label>}
      {phase === 'reselect' && needsAlt && <label>{t(language, 'imageAltRequired')}<input value={alt} onChange={(event) => setAlt(event.target.value)} /></label>}
      <div className="actions"><button disabled={phase === 'saving'} onClick={close}>{t(language, 'discardImage')}</button>
        {phase === 'conflict' ? <button onClick={() => void reloadForChoice()}>{t(language, 'imageReload')}</button> :
          <button className="primary" disabled={phase === 'saving' || !chosen || (needsAlt && !alt.trim())}
            onClick={() => void attach()}>{t(language, 'attachImage')}</button>}</div>
    </>}
  </section></div>;
}
