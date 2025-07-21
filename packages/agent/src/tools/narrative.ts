import type { PumpToken } from '@pumpmind/core';

const HYPE = ['ai', 'agent', 'pepe', 'trump', 'cat', 'dog', 'moon', 'sol'];

export async function scoreNarrative(token: PumpToken) {
  const hay = `${token.name} ${token.symbol}`.toLowerCase();
  const hits = HYPE.filter((w) => hay.includes(w));
  const score = Math.min(1, hits.length * 0.22 + (token.marketCapSol ? 0.1 : 0));
  return { score, summary: hits.length ? `narrative hits: ${hits.join(',')}` : 'neutral narrative' };
}
