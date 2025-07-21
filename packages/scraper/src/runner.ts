import { loadConfig, bus } from '@pumpmind/core';
import { PumpFunStream } from './pumpfun-ws';
import { normalizeNewToken } from './normalizer';

export function startScraper() {
  const cfg = loadConfig();
  const stream = new PumpFunStream(cfg.pumpfunWsUrl, (raw) => {
    const token = normalizeNewToken(raw);
    if (token) bus.emitNewToken(token);
  });
  stream.connect();
}
