import { useEffect, useRef } from 'react';
import { t } from '../i18n';
import type { Language } from '../types';

interface Props {
  language: Language | null;
  busy: boolean;
  conflict: boolean;
  error: string;
  onLanguage: (value: Language) => void;
  onClose: () => void;
  onReload: () => void;
}

export function Onboarding({ language, busy, conflict, error, onLanguage, onClose, onReload }: Props) {
  const dialog = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const previous = document.activeElement;
    dialog.current?.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus();
    return () => { if (previous instanceof HTMLElement) previous.focus(); };
  }, []);
  useEffect(() => {
    if (!busy && !dialog.current?.contains(document.activeElement))
      dialog.current?.querySelector<HTMLButtonElement>('button:not(:disabled)')?.focus();
  }, [busy, language, conflict]);
  return <div ref={dialog} className="overlay" role="dialog" aria-modal="true" aria-label="AURORA onboarding"
    onKeyDown={(event) => {
      if (event.key === 'Escape' && !busy && !conflict) { event.preventDefault(); onClose(); }
      if (event.key !== 'Tab') return;
      const buttons = Array.from(dialog.current?.querySelectorAll<HTMLButtonElement>('button:not(:disabled)') ?? []);
      const first = buttons[0]; const last = buttons.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }}>
    <div className="dialog onboarding">
      <button style={{ float: 'right' }} aria-label={language ? t(language, 'close') : 'Закрыть / Close'}
        disabled={busy || conflict} onClick={onClose}>×</button>
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
      {busy && <p role="status">{t(language ?? 'en', 'saving')}</p>}
      {error && !conflict && <p role="alert">{language ? t(language, 'onboardingSaveFailed')
        : 'Не удалось сохранить настройки. Повторите выбор языка или закрытие окна. / Could not save settings. Try choosing a language or closing again.'}</p>}
      {conflict && <><p role="alert">{t(language ?? 'en', 'preferencesConflict')}</p>
        <button disabled={busy} onClick={onReload}>{t(language ?? 'en', 'reloadPreferences')}</button></>}
    </div>
  </div>;
}
