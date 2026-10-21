import { useEffect, useRef, useState } from 'react';
import { MAX_RASTER_BYTES, RASTER_TYPES } from '../config';
import { t } from '../i18n';
import type { EditorDocument, Language } from '../types';

export type PhotoTarget = { kind: 'logo' } | { kind: 'section'; pageId: string; sectionId: string };
export type PhotoAttachOutcome = 'attached' | 'upload-failed' | 'save-failed' | 'target-changed';

interface TrayItem {
  id: string;
  file: File;
  preview: string;
  targetKey: string;
}

interface Props {
  language: Language;
  editor: EditorDocument;
  onAttach: (file: File, target: PhotoTarget) => Promise<PhotoAttachOutcome>;
  onClose: () => void;
}

const MAX_TRAY_ITEMS = 20;

function sectionKey(pageId: string, sectionId: string): string { return `${pageId}/${sectionId}`; }

function targetFor(editor: EditorDocument, key: string): PhotoTarget | null {
  if (key === 'logo') return { kind: 'logo' };
  for (const page of editor.pages) {
    for (const section of page.sections) {
      if (key === sectionKey(page.id, section.id)) {
        return { kind: 'section', pageId: page.id, sectionId: section.id };
      }
    }
  }
  return null;
}

export function PhotoTray({ language, editor, onAttach, onClose }: Props) {
  const [items, setItems] = useState<TrayItem[]>([]);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const urls = useRef(new Set<string>());
  const pending = useRef(false);

  useEffect(() => () => {
    for (const url of urls.current) URL.revokeObjectURL(url);
    urls.current.clear();
  }, []);

  function remove(item: TrayItem) {
    URL.revokeObjectURL(item.preview); urls.current.delete(item.preview);
    setItems((current) => current.filter((entry) => entry.id !== item.id));
  }

  function add(files: FileList | null) {
    const selected = Array.from(files ?? []);
    if (!selected.length) return;
    if (items.length + selected.length > MAX_TRAY_ITEMS || selected.some((file) =>
      !RASTER_TYPES.some((type) => type === file.type) || !file.size || file.size > MAX_RASTER_BYTES)) {
      setError(t(language, 'photoSelectionInvalid')); return;
    }
    const additions: TrayItem[] = [];
    const createdUrls: string[] = [];
    try {
      for (const file of selected) {
        const preview = URL.createObjectURL(file);
        createdUrls.push(preview);
        urls.current.add(preview);
        additions.push({ id: crypto.randomUUID(), file, preview, targetKey: '' });
      }
    } catch {
      for (const preview of createdUrls) {
        URL.revokeObjectURL(preview); urls.current.delete(preview);
      }
      setError(t(language, 'photoPreviewFailed')); return;
    }
    setItems((current) => [...current, ...additions]); setError('');
  }

  async function attach(item: TrayItem) {
    const target = targetFor(editor, item.targetKey);
    if (!target) { setError(t(language, 'photoTargetChanged')); return; }
    if (pending.current) return;
    pending.current = true; setPendingId(item.id); setError('');
    try {
      const outcome = await onAttach(item.file, target);
      if (outcome === 'attached') remove(item);
      else setError(t(language, outcome === 'upload-failed' ? 'photoUploadFailed'
        : outcome === 'save-failed' ? 'photoSaveFailed' : 'photoTargetChanged'));
    } catch { setError(t(language, 'photoSaveFailed')); }
    finally { pending.current = false; setPendingId(null); }
  }

  return <section className="photo-tray card" aria-label={t(language, 'photoTray')}>
    <div className="photo-tray-head"><div><span className="eyebrow">LOCAL PHOTOS</span>
      <h2>{t(language, 'photoTray')}</h2></div>
      <button type="button" disabled={pendingId !== null} onClick={onClose}>{t(language, 'close')}</button></div>
    <p>{t(language, 'photoTrayNote')}</p>
    <label>{t(language, 'photoChoose')}<input type="file" multiple
      accept="image/png,image/jpeg,image/gif,image/webp" disabled={pendingId !== null}
      onChange={(event) => { add(event.currentTarget.files); event.currentTarget.value = ''; }} /></label>
    <small>{t(language, 'photoLimits')}</small>
    {error && <p role="alert" className="photo-tray-error">{error}</p>}
    {items.length === 0 && <p className="muted">{t(language, 'photoEmpty')}</p>}
    <ul className="photo-tray-list">{items.map((item) => <li key={item.id} className="photo-tray-item">
      <img src={item.preview} alt="" />
      <div><strong>{item.file.name}</strong><small>{(item.file.size / 1024 / 1024).toFixed(2)} MiB</small>
        <label>{t(language, 'photoDestination')}<select value={item.targetKey} disabled={pendingId !== null}
          onChange={(event) => setItems((current) => current.map((entry) => entry.id === item.id
            ? { ...entry, targetKey: event.target.value } : entry))}>
          <option value="">{t(language, 'photoChooseDestination')}</option>
          <option value="logo">{t(language, 'imageLogoTarget')}</option>
          {editor.pages.flatMap((page) => page.sections.map((section) =>
            <option key={sectionKey(page.id, section.id)} value={sectionKey(page.id, section.id)}>
              {page.title || page.slug} / {section.heading || section.id}
            </option>))}
        </select></label>
        <div className="actions"><button type="button" disabled={pendingId !== null || !targetFor(editor, item.targetKey)}
          onClick={() => void attach(item)}>{pendingId === item.id ? t(language, 'photoAttaching') : t(language, 'photoAttach')}</button>
          <button type="button" disabled={pendingId !== null} onClick={() => remove(item)}>{t(language, 'remove')}</button></div>
      </div>
    </li>)}</ul>
  </section>;
}
