import { bus } from '@pumpmind/core';
import { planForToken } from './planner';

export function startAgentLoop() {
  bus.on('token:new', async (token) => {
    const decision = await planForToken(token);
    bus.emit('agent:decision', decision);
  });
}
