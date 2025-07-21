import type { PumpToken, MintAddress } from '@pumpmind/core';
import type { RawPumpEvent } from './pumpfun-ws';

export function normalizeNewToken(raw: RawPumpEvent): PumpToken | null {
  if (!raw.mint || !raw.name || !raw.symbol) return null;
  return {
    mint: raw.mint as MintAddress,
    name: raw.name,
    symbol: raw.symbol,
    creator: raw.traderPublicKey ?? 'unknown',
    createdAt: new Date(),
    marketCapSol: raw.marketCapSol,
  };
}
