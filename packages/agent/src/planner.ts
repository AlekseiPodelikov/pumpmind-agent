import type { PumpToken, AgentDecision } from '@pumpmind/core';
import { scoreNarrative } from './tools/narrative';
import { checkLiquidityRisk } from './tools/risk';
import { shortTermMemory } from './memory';

export async function planForToken(token: PumpToken): Promise<AgentDecision> {
  const narrative = await scoreNarrative(token);
  const risk = checkLiquidityRisk(token);
  const score = narrative.score * 0.6 + risk.score * 0.4;
  const action = score > 0.72 ? 'alert' : score > 0.45 ? 'watch' : 'skip';
  const decision: AgentDecision = {
    id: crypto.randomUUID(),
    mint: token.mint,
    action,
    score,
    rationale: `${narrative.summary}; risk=${risk.label}`,
    toolsUsed: ['narrative', 'risk'],
    createdAt: new Date(),
  };
  shortTermMemory.remember(token.mint, decision);
  return decision;
}

// 2025-07-22

// 2025-07-30

// 2025-08-29

// 2025-09-18

// 2025-10-10

// 2025-11-04

// 2025-11-25

// 2025-12-03

// 2026-01-27

// 2026-02-04

// 2026-03-11

// 2026-03-31

// 2026-04-22

// 2026-05-14

// 2026-05-29
