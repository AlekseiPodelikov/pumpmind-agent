import { createHash } from 'node:crypto';
export const shortHash = (s: string) => createHash('sha256').update(s).digest('hex').slice(0, 12);
