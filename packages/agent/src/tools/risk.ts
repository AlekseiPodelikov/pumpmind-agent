import type { PumpToken } from '@pumpmind/core';

export function checkLiquidityRisk(token: PumpToken) {
  const mcap = token.marketCapSol ?? 0;
  if (mcap < 5) return { score: 0.2, label: 'thin' };
  if (mcap < 30) return { score: 0.55, label: 'early' };
  return { score: 0.75, label: 'liquid-enough' };
}
