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
