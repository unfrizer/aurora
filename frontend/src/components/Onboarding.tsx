import { t } from '../i18n';
import type { Language } from '../types';

interface Props {
  language: Language | null;
  onLanguage: (value: Language) => void;
  onClose: () => void;
}

export function Onboarding({ language, onLanguage, onClose }: Props) {
  return <div className="overlay" role="dialog" aria-modal="true" aria-label="AURORA onboarding">
    <div className="dialog onboarding">
      <span className="eyebrow">AURORA · WORKSPACE</span>
      <h1>{language ? t(language, 'welcome') : 'AURORA / АВРОРА'}</h1>
      {!language ? <>
        <p>Choose your language / Выберите язык интерфейса</p>
        <div className="actions">
          <button onClick={() => onLanguage('ru')}>Русский</button>
          <button onClick={() => onLanguage('en')}>English</button>
        </div>
      </> : <>
        <p>{t(language, 'onboardingText')}</p>
        <p className="muted">{t(language, 'noGeneration')}</p>
        <button className="primary" onClick={onClose}>{t(language, 'start')}</button>
      </>}
    </div>
  </div>;
}
