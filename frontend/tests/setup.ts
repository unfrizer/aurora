import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(cleanup);

let sequence = 0;
Object.defineProperty(globalThis.crypto, 'randomUUID', {
  configurable: true,
  value: () => `00000000-0000-4000-8000-${String(++sequence).padStart(12, '0')}`,
});
