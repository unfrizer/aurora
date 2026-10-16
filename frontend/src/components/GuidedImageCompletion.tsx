import { useState } from 'react';
import { t } from '../i18n';
import type { EditorDocument, Language, ProjectDocument } from '../types';
import { ImageGeneration, type ImageSnapshot, type ImageTarget } from './ImageGeneration';

interface Props {
  language: Language;
  projectId: string;
  editor: EditorDocument;
  model: string;
  onSnapshot: () => Promise<ImageSnapshot | null>;
  onDocument: (document: ProjectDocument, editor: EditorDocument) => void;
  onLock: (locked: boolean) => void;
  onError: (error: unknown) => void;
  onExit: () => void;
}

interface PlannedImage {
  key: string;
  target: ImageTarget;
  label: string;
  prompt: string;
}

function keyOf(target: ImageTarget): string {
  return target.kind === 'logo' ? 'logo' : `${target.pageId}/${target.sectionId}`;
}

function planImages(editor: EditorDocument, language: Language): PlannedImage[] {
  const plan: PlannedImage[] = [];
  if (editor.brand.logo_path === null) plan.push({
    key: 'logo', target: { kind: 'logo' }, label: t(language, 'imageLogoTarget'),
    prompt: `Create a brand logo for "${editor.brand.name}". Tagline: "${editor.brand.tagline}". Language: ${editor.language}.`,
  });
  for (const page of editor.pages) {
    if (plan.length >= (editor.brand.logo_path === null ? 5 : 4)) break;
    const section = page.sections.find((item) => item.image_path === null);
    if (!section) continue;
    const target: ImageTarget = { kind: 'section', pageId: page.id, sectionId: section.id };
    plan.push({ key: keyOf(target), target, label: `${page.title} / ${section.heading}`,
      prompt: `Create an image for page "${page.heading}", section "${section.heading}", brand "${editor.brand.name}". Language: ${editor.language}.` });
  }
  return plan;
}

function targetState(editor: EditorDocument, target: ImageTarget): 'empty' | 'filled' | 'missing' {
  if (target.kind === 'logo') return editor.brand.logo_path === null ? 'empty' : 'filled';
  const section = editor.pages.find((page) => page.id === target.pageId)?.sections
    .find((item) => item.id === target.sectionId);
  return !section ? 'missing' : section.image_path === null ? 'empty' : 'filled';
}

export function GuidedImageCompletion({ language, projectId, editor, model, onSnapshot, onDocument,
  onLock, onError, onExit }: Props) {
  const [plan] = useState(() => planImages(editor, language));
  const [started, setStarted] = useState(false);
  const [skipped, setSkipped] = useState<ReadonlySet<string>>(() => new Set());
  const [attached, setAttached] = useState<ReadonlySet<string>>(() => new Set());
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const selected = plan.find((item) => item.key === selectedKey);
  const remaining = plan.filter((item) => !skipped.has(item.key) && targetState(editor, item.target) === 'empty');
  const filledCount = plan.filter((item) => !skipped.has(item.key) && targetState(editor, item.target) === 'filled').length;
  const missingCount = plan.filter((item) => !skipped.has(item.key) && targetState(editor, item.target) === 'missing').length;
  const current = remaining[0];
  const allowedTargets = remaining.map((item) => item.target);
  const status = (item: PlannedImage) => skipped.has(item.key) ? t(language, 'guidedSkipped') :
    targetState(editor, item.target) === 'missing' ? t(language, 'guidedMissing') :
      targetState(editor, item.target) === 'filled' ?
        t(language, attached.has(item.key) ? 'guidedAttached' : 'guidedFilled') : t(language, 'guidedPending');

  function open(item: PlannedImage) { onLock(true); setSelectedKey(item.key); }
  function close() { setSelectedKey(null); onLock(false); }
  function skip(item: PlannedImage) { setSkipped((previous) => new Set(previous).add(item.key)); }
  function markAttached(target: ImageTarget) {
    setAttached((previous) => new Set(previous).add(keyOf(target)));
  }

  return <>
    <main className="guided-page" inert={selected !== undefined}>
      <span className="eyebrow">IMAGE COMPLETION</span><h1>{t(language, 'guidedTitle')}</h1>
      {!started ? <section className="card guided-intro">
        <p>{t(language, 'guidedIntro')}</p>
        <p>{t(language, 'guidedInitialCount')}: {plan.length}. {t(language, 'guidedRetryCost')}</p>
        <div className="actions"><button className="primary" disabled={plan.length === 0}
          onClick={() => setStarted(true)}>{t(language, 'guidedStart')}</button>
          <button onClick={onExit}>{t(language, 'guidedWorkspace')}</button></div>
      </section> : <section className="card guided-plan">
        <p>{t(language, 'guidedProgress')}: {filledCount} {t(language, 'guidedFilled')},
          {' '}{skipped.size} {t(language, 'guidedSkipped')}, {remaining.length} {t(language, 'guidedPending')},
          {' '}{missingCount} {t(language, 'guidedMissing')}.</p>
        <ol>{plan.map((item) => <li key={item.key}><span>{item.label}</span><strong>{status(item)}</strong></li>)}</ol>
        {current ? <div className="guided-current">
          <h2>{current.label}</h2>
          <p>{t(language, 'guidedProposedPrompt')}</p><p className="guided-prompt">{current.prompt}</p>
          <div className="actions"><button className="primary" onClick={() => open(current)}>{t(language, 'guidedReviewImage')}</button>
            <button onClick={() => skip(current)}>{t(language, 'guidedSkip')}</button></div>
        </div> : <p role="status">{skipped.size > 0 || missingCount > 0
          ? t(language, 'guidedPartial') : t(language, 'guidedDone')}</p>}
        <button onClick={onExit}>{t(language, 'guidedWorkspace')}</button>
      </section>}
      {plan.length === 0 && <p role="status">{t(language, 'guidedDone')}</p>}
    </main>
    {selected && <ImageGeneration key={selected.key} language={language} projectId={projectId}
      target={selected.target} targetLabel={selected.label} model={model} initialPrompt={selected.prompt}
      allowedTargets={allowedTargets} requireEmptyTarget guided onSnapshot={onSnapshot}
      onDocument={onDocument} onError={onError} onAttached={markAttached} onClose={close} />}
  </>;
}
