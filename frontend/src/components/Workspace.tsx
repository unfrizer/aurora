import { useEffect, useRef, useState } from 'react';
import { deleteRaster, previewUrl, rasterUrl, uploadRaster } from '../api';
import { assetName, move, nextPageSlug, replacePage, replaceSection } from '../editor';
import { t } from '../i18n';
import type { EditorDocument, EditorPage, EditorSection, Language } from '../types';
import { TextAssist } from './TextAssist';

interface Props {
  language: Language;
  projectId: string;
  projectName: string;
  editor: EditorDocument;
  model: string;
  dirty: boolean;
  saving: boolean;
  onCommit: (next: EditorDocument) => Promise<boolean>;
  onFlush: () => Promise<string | null>;
  onRename: (name: string) => Promise<boolean>;
  onReload: () => Promise<void>;
  onError: (error: unknown) => void;
}

function Field({ label, value, onCommit, multiline = false, type = 'text', disabled = false }: {
  label: string; value: string; onCommit: (value: string) => void;
  multiline?: boolean; type?: string; disabled?: boolean;
}) {
  return <label className="field">{label}{multiline
    ? <textarea key={value} defaultValue={value} disabled={disabled} rows={5} onBlur={(event) => { if (event.target.value !== value) onCommit(event.target.value); }} />
    : <input key={value} type={type} defaultValue={value} disabled={disabled} onBlur={(event) => { if (event.target.value !== value) onCommit(event.target.value); }} />}</label>;
}

function assetReferenced(editor: EditorDocument, path: string): boolean {
  return editor.brand.logo_path === path || editor.pages.some((page) => page.sections.some((section) => section.image_path === path));
}

function withSectionImage(editor: EditorDocument, pageId: string, sectionId: string, path: string | null): EditorDocument {
  const page = editor.pages.find((item) => item.id === pageId);
  const section = page?.sections.find((item) => item.id === sectionId);
  if (!page || !section) throw new Error('The selected section is no longer available');
  return replaceSection(editor, pageId, { ...section, image_path: path });
}

export function Workspace({ language, projectId, projectName, editor, model, dirty, saving,
  onCommit, onFlush, onRename, onReload, onError }: Props) {
  const [pageId, setPageId] = useState(editor.pages[0]?.id ?? '');
  const [sectionId, setSectionId] = useState('');
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);
  const [mobile, setMobile] = useState(false);
  const [preview, setPreview] = useState('');
  const [newPage, setNewPage] = useState('');
  const [newSection, setNewSection] = useState('');
  const [rename, setRename] = useState(projectName);
  const latestEditor = useRef(editor);
  latestEditor.current = editor;
  const page = editor.pages.find((item) => item.id === pageId) ?? editor.pages[0];
  const section = page?.sections.find((item) => item.id === sectionId) ?? page?.sections[0];
  useEffect(() => { if (page && page.id !== pageId) setPageId(page.id); }, [page, pageId]);
  useEffect(() => { if (section && section.id !== sectionId) setSectionId(section.id); }, [section, sectionId]);

  function commit(next: EditorDocument) { setPreview(''); void onCommit(next); }
  function changePage(updated: EditorPage) { commit(replacePage(editor, updated)); }
  function changeSection(updated: EditorSection) { if (page) commit(replaceSection(editor, page.id, updated)); }

  async function image(file: File | undefined, old: string | null, apply: (current: EditorDocument, path: string | null) => EditorDocument) {
    if (!file) return;
    try {
      const path = await uploadRaster(projectId, file);
      const next = apply(latestEditor.current, path);
      const saved = await onCommit(next);
      if (saved && old && old !== path && !assetReferenced(next, old)) {
        const name = assetName(old);
        if (name) await deleteRaster(projectId, name);
      }
    } catch (error) { onError(error); }
  }

  async function removeImage(old: string | null, apply: (current: EditorDocument, path: string | null) => EditorDocument) {
    if (!old) return;
    const next = apply(latestEditor.current, null);
    const saved = await onCommit(next);
    if (saved && !assetReferenced(next, old)) {
      const name = assetName(old);
      if (name) try { await deleteRaster(projectId, name); } catch (error) { onError(error); }
    }
  }

  async function showPreview() {
    const timestamp = await onFlush();
    if (timestamp && page) setPreview(`${previewUrl(projectId, page.slug)}?v=${encodeURIComponent(timestamp)}`);
  }

  return <main className={`workspace ${leftOpen ? '' : 'left-collapsed'} ${rightOpen ? '' : 'right-collapsed'}`}>
    <aside className="side left">
      <div className="side-head"><h2>{t(language, 'pages')}</h2><button aria-label={`Toggle ${t(language, 'pages')}`} onClick={() => setLeftOpen(!leftOpen)}>{leftOpen ? '‹' : '›'}</button></div>
      {leftOpen && <>
        <ol className="page-list">{editor.pages.map((item, index) => <li key={item.id} className={item.id === page?.id ? 'selected' : ''}>
          <button className="page-select" onClick={() => { setPageId(item.id); setSectionId(''); setPreview(''); }}>{item.title || item.slug}</button>
          <div className="tiny-actions">
            <button aria-label={`${t(language, 'up')} ${item.title}`} disabled={index === 0 || item.slug === 'index' || editor.pages[index - 1]?.slug === 'index'} onClick={() => commit({ ...editor, pages: move(editor.pages, index, -1) })}>↑</button>
            <button aria-label={`${t(language, 'down')} ${item.title}`} disabled={index === editor.pages.length - 1 || item.slug === 'index'} onClick={() => commit({ ...editor, pages: move(editor.pages, index, 1) })}>↓</button>
            <button aria-label={`${t(language, 'remove')} ${item.title}`} disabled={item.slug === 'index' || editor.pages.length <= 1} onClick={() => commit({ ...editor, pages: editor.pages.filter((other) => other.id !== item.id) })}>×</button>
          </div>
        </li>)}</ol>
        <form className="add-form" onSubmit={(event) => { event.preventDefault(); if (!newPage.trim()) return;
          const id = crypto.randomUUID();
          commit({ ...editor, pages: [...editor.pages, { id, slug: nextPageSlug(editor), title: newPage.trim(), meta_description: '', heading: newPage.trim(), sections: [] }] });
          setPageId(id); setNewPage(''); }}>
          <input aria-label={t(language, 'pageTitle')} placeholder={t(language, 'pageTitle')} value={newPage} onChange={(event) => setNewPage(event.target.value)} />
          <button disabled={!newPage.trim()}>{t(language, 'addPage')}</button>
        </form>
      </>}
    </aside>
    <section className="canvas">
      <div className="canvas-toolbar"><div><span className="eyebrow">EDITOR / {page?.slug ?? '—'}</span><h1>{projectName}</h1></div>
        <div className="actions"><span className={`save-state ${dirty ? 'dirty' : ''}`} role="status">{saving ? t(language, 'saving') : dirty ? t(language, 'unsaved') : t(language, 'saved')}</span>
          <button onClick={() => void onFlush()}>{t(language, 'save')}</button>
          <button onClick={() => void onReload()}>{t(language, 'reload')}</button></div></div>
      {!page ? <p>{t(language, 'badEditor')}</p> : <>
        <div className="tabline"><button className={preview ? '' : 'active'} onClick={() => setPreview('')}>{t(language, 'workspace')}</button>
          <button className={preview ? 'active' : ''} onClick={() => void showPreview()}>{t(language, 'preview')}</button>
          {preview && <><button onClick={() => setMobile(false)}>{t(language, 'desktop')}</button><button onClick={() => setMobile(true)}>{t(language, 'mobile')}</button>
            <a href={preview} target="_blank" rel="noopener noreferrer">{t(language, 'browser')}</a></>}</div>
        {preview ? <div className={`preview-frame ${mobile ? 'mobile' : ''}`}><iframe title={t(language, 'preview')} sandbox="allow-same-origin" src={preview} /></div> : <div className="editor-surface">
          <div className="page-title"><span className="eyebrow">PAGE SETTINGS</span>
            <Field label={t(language, 'title')} value={page.title} onCommit={(value) => changePage({ ...page, title: value })} />
            <Field label={t(language, 'heading')} value={page.heading} onCommit={(value) => changePage({ ...page, heading: value })} />
            <Field label={t(language, 'slug')} value={page.slug} disabled={page.slug === 'index'} onCommit={(value) => changePage({ ...page, slug: value })} />
            <Field label={t(language, 'description')} value={page.meta_description} multiline onCommit={(value) => changePage({ ...page, meta_description: value })} />
          </div>
          <div className="section-list"><div className="section-list-head"><span className="eyebrow">CONTENT BLOCKS</span><strong>{page.sections.length}</strong></div>
            {page.sections.map((item, index) => <article className={`section-card ${item.id === section?.id ? 'selected' : ''}`} key={item.id} onClick={() => setSectionId(item.id)}>
              <div className="section-actions"><span>0{index + 1} / SECTION</span><div className="tiny-actions">
                <button aria-label={`${t(language, 'up')} ${item.heading}`} disabled={index === 0} onClick={() => changePage({ ...page, sections: move(page.sections, index, -1) })}>↑</button>
                <button aria-label={`${t(language, 'down')} ${item.heading}`} disabled={index === page.sections.length - 1} onClick={() => changePage({ ...page, sections: move(page.sections, index, 1) })}>↓</button>
                <button aria-label={`${t(language, 'remove')} ${item.heading}`} onClick={() => changePage({ ...page, sections: page.sections.filter((other) => other.id !== item.id) })}>×</button>
              </div></div>
              <Field label={t(language, 'heading')} value={item.heading} onCommit={(value) => changeSection({ ...item, heading: value })} />
              <Field label={t(language, 'body')} value={item.body} multiline onCommit={(value) => changeSection({ ...item, body: value })} />
              {item.image_path && <img className="asset-preview" src={rasterUrl(projectId, item.image_path)} alt={item.image_alt} />}
              <Field label={t(language, 'imageAlt')} value={item.image_alt} onCommit={(value) => changeSection({ ...item, image_alt: value })} />
              <div className="actions"><label className="file-button">{t(language, 'upload')}<input type="file" accept="image/png,image/jpeg,image/gif,image/webp" onChange={(event) => void image(event.target.files?.[0], item.image_path, (current, path) => withSectionImage(current, page.id, item.id, path))} /></label>
                <button disabled={!item.image_path} onClick={() => void removeImage(item.image_path, (current, path) => withSectionImage(current, page.id, item.id, path))}>{t(language, 'removeImage')}</button></div>
            </article>)}
            <form className="add-form" onSubmit={(event) => { event.preventDefault(); if (!newSection.trim()) return;
              const id = crypto.randomUUID();
              changePage({ ...page, sections: [...page.sections, { id, heading: newSection.trim(), body: '', image_path: null, image_alt: '' }] });
              setSectionId(id); setNewSection(''); }}>
              <input aria-label={t(language, 'sectionTitle')} placeholder={t(language, 'sectionTitle')} value={newSection} onChange={(event) => setNewSection(event.target.value)} />
              <button disabled={!newSection.trim()}>{t(language, 'addSection')}</button>
            </form>
          </div>
        </div>}
      </>}
    </section>
    <aside className="side right"><div className="side-head"><h2>{t(language, 'inspector')}</h2><button aria-label={`Toggle ${t(language, 'inspector')}`} onClick={() => setRightOpen(!rightOpen)}>{rightOpen ? '›' : '‹'}</button></div>
      {rightOpen && <div className="inspector-content">
        <section className="card"><span className="eyebrow">PROJECT</span>
          <label className="field">{t(language, 'projectName')}<input value={rename} onChange={(event) => setRename(event.target.value)}
            onBlur={() => { if (rename !== projectName) void onRename(rename).then((saved) => { if (!saved) setRename(projectName); }); }} /></label>
        </section>
        <section className="card"><span className="eyebrow">IDENTITY</span><h3>{t(language, 'brand')}</h3>
          <Field label={t(language, 'brandName')} value={editor.brand.name} onCommit={(value) => commit({ ...editor, brand: { ...editor.brand, name: value } })} />
          <Field label={t(language, 'tagline')} value={editor.brand.tagline} onCommit={(value) => commit({ ...editor, brand: { ...editor.brand, tagline: value } })} />
          <Field label={t(language, 'primary')} value={editor.brand.primary_color} onCommit={(value) => commit({ ...editor, brand: { ...editor.brand, primary_color: value } })} />
          <Field label={t(language, 'secondary')} value={editor.brand.secondary_color} onCommit={(value) => commit({ ...editor, brand: { ...editor.brand, secondary_color: value } })} />
          <label className="field">{t(language, 'font')}<select value={editor.brand.font_family} onChange={(event) => commit({ ...editor, brand: { ...editor.brand, font_family: event.target.value as EditorDocument['brand']['font_family'] } })}>
            <option value="system">System</option><option value="serif">Serif</option><option value="monospace">Monospace</option></select></label>
          {editor.brand.logo_path && <img className="asset-preview" src={rasterUrl(projectId, editor.brand.logo_path)} alt={editor.brand.name} />}
          <div className="actions"><label className="file-button">{t(language, 'logo')}<input type="file" accept="image/png,image/jpeg,image/gif,image/webp" onChange={(event) => void image(event.target.files?.[0], editor.brand.logo_path, (current, path) => ({ ...current, brand: { ...current.brand, logo_path: path } }))} /></label>
            <button disabled={!editor.brand.logo_path} onClick={() => void removeImage(editor.brand.logo_path, (current, path) => ({ ...current, brand: { ...current.brand, logo_path: path } }))}>{t(language, 'removeImage')}</button></div>
        </section>
        {section && <TextAssist key={section.id} language={language} section={section} model={model} onAccept={(body) => changeSection({ ...section, body })} onError={onError} />}
      </div>}
    </aside>
  </main>;
}
