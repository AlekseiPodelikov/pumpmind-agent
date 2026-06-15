import type { AgentDecision, SignalPayload } from '@pumpmind/core';
import { dedupe } from './dedupe';
import { toSignal } from './formatters';

export type Sink = (payload: SignalPayload) => Promise<void>;

export class SignalRouter {
  constructor(private sinks: Sink[]) {}

  async route(decision: AgentDecision, symbol: string) {
    if (decision.action === 'skip') return;
    if (!dedupe.allow(decision.mint)) return;
    const payload = toSignal(decision, symbol);
    await Promise.all(this.sinks.map((s) => s(payload)));
  }
}

// 2025-07-24

// 2025-08-25

// 2025-09-13

// 2025-10-06

// 2025-10-14

// 2025-11-06

// 2025-11-27

// 2025-12-10

// 2026-01-29

// 2026-02-11

// 2026-03-13

// 2026-04-02

// 2026-04-24

// 2026-05-25

// 2026-06-15
