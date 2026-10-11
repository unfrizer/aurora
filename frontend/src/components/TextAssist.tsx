import { useState } from 'react';
import { generateText } from '../api';
import { t } from '../i18n';
import type { EditorSection, Language } from '../types';

interface Props {
  language: Language;
  section: EditorSection;
  model: string;
  onAccept: (body: string) => void;
  onError: (error: unknown) => void;
}

export function TextAssist({ language, section, model, onAccept, onError }: Props) {
  const [instruction, setInstruction] = useState('');
  const [proposal, setProposal] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function run() {
    if (!instruction.trim() || !model.trim()) return;
    setBusy(true); setProposal(null);
    try {
      const job = await generateText(model.trim(), section.body || section.heading, instruction.trim());
      if (job.status === 'completed' && job.result) setProposal(job.result.output_text);
      else onError(new Error('Generation failed'));
    } catch (error) { onError(error); }
    finally { setBusy(false); }
  }
  return <section className="assist card" aria-label={t(language, 'textAssist')}>
    <span className="eyebrow">TEXT ASSIST</span><h3>{t(language, 'textAssist')}</h3>
    <p className="muted">{section.heading}</p>
    <label>{t(language, 'instruction')}<textarea value={instruction} onChange={(event) => setInstruction(event.target.value)} rows={3} /></label>
    <button disabled={busy || !instruction.trim() || !model.trim()} onClick={() => void run()}>{t(language, 'generate')}</button>
    {proposal !== null && <div className="proposal"><strong>{t(language, 'proposal')}</strong><p>{proposal}</p>
      <button className="primary" onClick={() => { onAccept(proposal); setProposal(null); }}>{t(language, 'accept')}</button></div>}
  </section>;
}
