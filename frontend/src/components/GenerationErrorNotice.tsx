import { t, type Label } from '../i18n';
import type { Language } from '../types';

export function GenerationErrorNotice({ language, title, failure }: {
  language: Language; title: string; failure: { category: string; retryable: boolean };
}) {
  const labels: Record<string, Label> = {
    authentication: 'aiAuthentication', network: 'aiNetwork',
    invalid_response: 'aiInvalidResponse', remote: 'aiRemote',
  };
  const limited = failure.category === 'rate_limited';
  const label = limited ? failure.retryable ? 'aiRateLimit' : 'aiQuota'
    : Object.hasOwn(labels, failure.category) ? labels[failure.category]! : 'aiRemote';
  return <div className="generation-error">
    <p role="alert">{title}: {t(language, label)}</p>
    {limited && <p className="actions">
      <a href="https://platform.openai.com/settings/organization/billing/overview" target="_blank" rel="noopener noreferrer">{t(language, 'aiBilling')}</a>
      <a href="https://platform.openai.com/settings/organization/limits" target="_blank" rel="noopener noreferrer">{t(language, 'aiLimits')}</a>
    </p>}
  </div>;
}
