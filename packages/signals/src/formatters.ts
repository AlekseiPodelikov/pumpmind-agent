import type { AgentDecision, SignalPayload } from '@pumpmind/core';

export function toSignal(decision: AgentDecision, symbol: string): SignalPayload {
  const severity = decision.score > 0.8 ? 'high' : decision.score > 0.55 ? 'medium' : 'low';
  return {
    decisionId: decision.id,
    mint: decision.mint,
    symbol,
    headline: `[${decision.action.toUpperCase()}] ${symbol} score=${decision.score.toFixed(2)}`,
    severity,
    metadata: { rationale: decision.rationale, tools: decision.toolsUsed },
  };
}
