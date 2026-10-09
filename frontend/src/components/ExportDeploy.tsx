import { useState } from 'react';
import { ApiError, deployNetlify, exportZip } from '../api';
import { t } from '../i18n';
import type { Language } from '../types';

interface Props {
  language: Language;
  projectId: string;
  ready: () => Promise<string | null>;
  onError: (error: unknown) => void;
}

export function ExportDeploy({ language, projectId, ready, onError }: Props) {
  const [siteId, setSiteId] = useState('');
  const [url, setUrl] = useState('');
  const [recovery, setRecovery] = useState<{ site_id: string | null; deploy_id: string | null } | null>(null);
  const [busy, setBusy] = useState(false);
  async function zip() {
    setBusy(true);
    try {
      const expected = await ready();
      if (!expected) return;
      const blob = await exportZip(projectId, expected);
      const objectUrl = URL.createObjectURL(blob);
      try {
        const link = document.createElement('a');
        link.href = objectUrl; link.download = 'aurora-site.zip';
        document.body.append(link); link.click(); link.remove();
      } finally { window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0); }
    } catch (error) { onError(error); }
    finally { setBusy(false); }
  }
  async function deploy() {
    if (!window.confirm(t(language, 'deployConfirm'))) return;
    setBusy(true); setRecovery(null); setUrl('');
    try {
      const expected = await ready();
      if (!expected) return;
      const result = await deployNetlify(projectId, expected, siteId.trim() || null);
      setUrl(result.public_url); setSiteId(result.site_id);
    } catch (error) {
      if (error instanceof ApiError && error.recovery) setRecovery(error.recovery);
      onError(error);
    } finally { setBusy(false); }
  }
  return <main className="export-page">
    <span className="eyebrow">PUBLISH / 03</span><h1>{t(language, 'export')}</h1>
    <div className="card"><h2>Static site</h2><p>{t(language, 'noFolder')}</p>
      <button className="primary" disabled={busy} onClick={() => void zip()}>{t(language, 'zip')}</button></div>
    <div className="card"><h2>Netlify</h2>
      <label>{t(language, 'siteId')}<input value={siteId} onChange={(event) => setSiteId(event.target.value)} /></label>
      <button disabled={busy} onClick={() => void deploy()}>{t(language, 'deploy')}</button>
      {url && <p>{t(language, 'deployed')}: <a href={url} rel="noopener noreferrer" target="_blank">{url}</a></p>}
      {recovery && <p role="alert">{t(language, 'recovery')}<br />site_id: {recovery.site_id ?? '—'}<br />deploy_id: {recovery.deploy_id ?? '—'}</p>}
    </div>
  </main>;
}
