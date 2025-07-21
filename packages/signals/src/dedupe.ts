import type { MintAddress } from '@pumpmind/core';

const seen = new Map<MintAddress, number>();
const TTL_MS = 15 * 60 * 1000;

export const dedupe = {
  allow(mint: MintAddress) {
    const now = Date.now();
    const prev = seen.get(mint);
    if (prev && now - prev < TTL_MS) return false;
    seen.set(mint, now);
    return true;
  },
};
