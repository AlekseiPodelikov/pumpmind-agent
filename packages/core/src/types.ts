export type MintAddress = string & { readonly __brand: 'MintAddress' };

export interface PumpToken {
  mint: MintAddress;
  name: string;
  symbol: string;
  creator: string;
  createdAt: Date;
  marketCapSol?: number;
  bondingCurveProgress?: number;
}

export interface AgentDecision {
  id: string;
  mint: MintAddress;
  action: 'watch' | 'alert' | 'skip' | 'execute';
  score: number;
  rationale: string;
  toolsUsed: string[];
  createdAt: Date;
}

export interface SignalPayload {
  decisionId: string;
  mint: MintAddress;
  symbol: string;
  headline: string;
  severity: 'low' | 'medium' | 'high';
  metadata: Record<string, unknown>;
}

// 2025-07-21

// 2025-07-28
