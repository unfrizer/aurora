import { useEffect, useRef, useState } from 'react';
import { credentialStatus, deleteCredential, setCredential } from '../api';
import { t } from '../i18n';
import { validPreferenceModel, type Language } from '../types';

type SecretName = 'openai_api_key' | 'netlify_token';

interface Props {
  language: Language;
  model: string;
  imageModel: string;
  projectsDirectory: string;
  busy: boolean;
  onSave: (language: Language, model: string, imageModel: string) => Promise<'ok' | 'conflict' | 'error'>;
  onReload: () => Promise<{ preferences: { language: Language | null; general_model: string; image_model: string } } | null>;
  onError: (error: unknown) => void;
}

function Secret({ name, label, language, onError }: { name: SecretName; label: string; language: Language; onError: (error: unknown) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [configured, setConfigured] = useState(false);
  const [busy, setBusy] = useState(false);
  useEffect(() => { void credentialStatus(name).then(setConfigured).catch(onError); }, [name, onError]);
  async function change(remove: boolean) {
    const value = input.current?.value ?? '';
    if (!remove && !value) return;
    setBusy(true);
    try {
      if (remove) await deleteCredential(name);
      else await setCredential(name, value);
      setConfigured(!remove);
    } catch (error) { onError(error); }
    finally { if (input.current) input.current.value = ''; setBusy(false); }
  }
  return <div className="setting-secret">
    <div><strong>{label}</strong><span className={configured ? 'badge good' : 'badge'}>{configured ? t(language, 'connected') : t(language, 'disconnected')}</span></div>
    <div className="actions"><input ref={input} type="password" autoComplete="off" aria-label={label} />
      <button disabled={busy} onClick={() => void change(false)}>{t(language, 'connect')}</button>
      <button disabled={busy || !configured} onClick={() => void change(true)}>{t(language, 'disconnect')}</button></div>
  </div>;
}

export function Settings({ language, model, imageModel, projectsDirectory, busy, onSave, onReload, onError }: Props) {
  const [draftLanguage, setDraftLanguage] = useState(language);
  const [draftModel, setDraftModel] = useState(model);
  const [draftImageModel, setDraftImageModel] = useState(imageModel);
  const [status, setStatus] = useState<'none' | 'saved' | 'failed' | 'conflict'>('none');
  useEffect(() => {
    setDraftLanguage(language); setDraftModel(model); setDraftImageModel(imageModel);
  }, [language, model, imageModel]);

  async function save() {
    const outcome = await onSave(draftLanguage, draftModel, draftImageModel);
    setStatus(outcome === 'ok' ? 'saved' : outcome === 'conflict' ? 'conflict' : 'failed');
  }

  async function reload() {
    if (!window.confirm(t(language, 'discardSettingsConfirm'))) return;
    const fresh = await onReload();
    if (!fresh) return;
    setDraftLanguage(fresh.preferences.language ?? 'en');
    setDraftModel(fresh.preferences.general_model);
    setDraftImageModel(fresh.preferences.image_model);
    setStatus('none');
  }

  return <main className="settings-page">
    <span className="eyebrow">PREFERENCES / 02</span><h1>{t(language, 'settings')}</h1>
    <p className="muted">{t(language, 'settingsNote')}</p>
    <div className="card settings-card">
      <label>{t(language, 'chooseLanguage')}
        <select value={draftLanguage} onChange={(event) => { setDraftLanguage(event.target.value as Language); if (status !== 'conflict') setStatus('none'); }}>
          <option value="ru">Русский</option><option value="en">English</option>
        </select>
      </label>
      <label>{t(language, 'model')}<input value={draftModel} onChange={(event) => { setDraftModel(event.target.value); if (status !== 'conflict') setStatus('none'); }} /></label>
      <label>{t(language, 'imageModel')}<input value={draftImageModel} onChange={(event) => { setDraftImageModel(event.target.value); if (status !== 'conflict') setStatus('none'); }} /></label>
      <label>{t(language, 'projectsDirectory')}<output>{projectsDirectory}</output></label>
      <div className="actions">
        <button className="primary" disabled={busy || status === 'conflict' || !validPreferenceModel(draftModel) || !validPreferenceModel(draftImageModel)}
          onClick={() => void save()}>{t(language, 'savePreferences')}</button>
        {status === 'conflict' && <button onClick={() => void reload()}>{t(language, 'reloadPreferences')}</button>}
      </div>
      {status === 'saved' && <p role="status">{t(language, 'saved')}</p>}
      {status === 'failed' && <p role="alert">{t(language, 'preferencesSaveFailed')}</p>}
      {status === 'conflict' && <p role="alert">{t(language, 'preferencesConflict')}</p>}
      <Secret name="openai_api_key" label={t(language, 'openai')} language={language} onError={onError} />
      <Secret name="netlify_token" label={t(language, 'netlify')} language={language} onError={onError} />
    </div>
  </main>;
}
