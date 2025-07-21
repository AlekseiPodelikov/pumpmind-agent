import type { AgentDecision, MintAddress } from '@pumpmind/core';

class ShortTermMemory {
  private map = new Map<MintAddress, AgentDecision>();

  remember(mint: MintAddress, d: AgentDecision) {
    this.map.set(mint, d);
    if (this.map.size > 500) {
      const first = this.map.keys().next().value;
      if (first) this.map.delete(first);
    }
  }

  get(mint: MintAddress) { return this.map.get(mint); }
}

export const shortTermMemory = new ShortTermMemory();
