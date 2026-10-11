import { useEffect, useRef, useState } from 'react';
import { credentialStatus, deleteCredential, setCredential } from '../api';
import { t } from '../i18n';
import type { Language } from '../types';

type SecretName = 'openai_api_key' | 'netlify_token';

interface Props {
  language: Language;
  onLanguage: (value: Language) => void;
  model: string;
  onModel: (value: string) => void;
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

export function Settings({ language, onLanguage, model, onModel, onError }: Props) {
  return <main className="settings-page">
    <span className="eyebrow">PREFERENCES / 02</span><h1>{t(language, 'settings')}</h1>
    <p className="muted">{t(language, 'settingsNote')}</p>
    <div className="card settings-card">
      <label>{t(language, 'chooseLanguage')}
        <select value={language} onChange={(event) => onLanguage(event.target.value as Language)}>
          <option value="ru">Русский</option><option value="en">English</option>
        </select>
      </label>
      <label>{t(language, 'model')}<input value={model} onChange={(event) => onModel(event.target.value)} /></label>
      <Secret name="openai_api_key" label={t(language, 'openai')} language={language} onError={onError} />
      <Secret name="netlify_token" label={t(language, 'netlify')} language={language} onError={onError} />
    </div>
  </main>;
}
