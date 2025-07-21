import { EventEmitter } from 'node:events';
import type { PumpToken, AgentDecision } from './types';

export type BusEvents = {
  'token:new': (token: PumpToken) => void;
  'agent:decision': (decision: AgentDecision) => void;
  'signal:emit': (payload: unknown) => void;
};

export class EventBus extends EventEmitter {
  emitNewToken(token: PumpToken) { this.emit('token:new', token); }
  emitDecision(decision: AgentDecision) { this.emit('agent:decision', decision); }
}

export const bus = new EventBus();
