import { t } from '../i18n';
import type { Language } from '../types';

interface Props {
  language: Language | null;
  busy: boolean;
  conflict: boolean;
  onLanguage: (value: Language) => void;
  onClose: () => void;
  onReload: () => void;
}

export function Onboarding({ language, busy, conflict, onLanguage, onClose, onReload }: Props) {
  return <div className="overlay" role="dialog" aria-modal="true" aria-label="AURORA onboarding">
    <div className="dialog onboarding">
      <span className="eyebrow">AURORA · WORKSPACE</span>
      <h1>{language ? t(language, 'welcome') : 'AURORA / АВРОРА'}</h1>
      {!language ? <>
        <p>Choose your language / Выберите язык интерфейса</p>
        <div className="actions">
          <button disabled={busy || conflict} onClick={() => onLanguage('ru')}>Русский</button>
          <button disabled={busy || conflict} onClick={() => onLanguage('en')}>English</button>
        </div>
      </> : <>
        <p>{t(language, 'onboardingText')}</p>
        <p className="muted">{t(language, 'noGeneration')}</p>
        <button className="primary" disabled={busy || conflict} onClick={onClose}>{t(language, 'start')}</button>
      </>}
      {conflict && <><p role="alert">{t(language ?? 'en', 'preferencesConflict')}</p>
        <button disabled={busy} onClick={onReload}>{t(language ?? 'en', 'reloadPreferences')}</button></>}
    </div>
  </div>;
}
