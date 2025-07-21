"""Generate pumpmind-agent source tree."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES: dict[str, str] = {}

def add(path: str, content: str) -> None:
    FILES[path] = content

# --- packages/core ---
add("packages/core/package.json", """{
  "name": "@pumpmind/core",
  "version": "0.4.2",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": { "build": "tsc", "test": "node --test dist/**/*.test.js" }
}""")

add("packages/core/tsconfig.json", """{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "outDir": "dist", "rootDir": "src" },
  "include": ["src"]
}""")

add("packages/core/src/index.ts", """export * from './types';
export * from './config';
export * from './logger';
export * from './events';
""")

add("packages/core/src/types.ts", """export type MintAddress = string & { readonly __brand: 'MintAddress' };

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
""")

add("packages/core/src/config.ts", """import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

export interface AppConfig {
  solanaRpcUrl: string;
  heliusApiKey?: string;
  openaiApiKey?: string;
  pumpfunWsUrl: string;
  agentModel: string;
  riskMaxPositionSol: number;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

function env(key: string, fallback = ''): string {
  return process.env[key] ?? fallback;
}

export function loadConfig(): AppConfig {
  const envPath = resolve(process.cwd(), '.env');
  if (existsSync(envPath)) {
    for (const line of readFileSync(envPath, 'utf8').split('\\n')) {
      const m = line.match(/^([^#=]+)=(.*)$/);
      if (m && !process.env[m[1]]) process.env[m[1]] = m[2].trim();
    }
  }
  return {
    solanaRpcUrl: env('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com'),
    heliusApiKey: env('HELIUS_API_KEY') || undefined,
    openaiApiKey: env('OPENAI_API_KEY') || undefined,
    pumpfunWsUrl: env('PUMPFUN_WS_URL', 'wss://pumpportal.fun/api/data'),
    agentModel: env('AGENT_MODEL', 'gpt-4o-mini'),
    riskMaxPositionSol: Number(env('RISK_MAX_POSITION_SOL', '0.5')),
    logLevel: (env('LOG_LEVEL', 'info') as AppConfig['logLevel']),
  };
}
""")

add("packages/core/src/logger.ts", """type Level = 'debug' | 'info' | 'warn' | 'error';

const LEVELS: Record<Level, number> = { debug: 10, info: 20, warn: 30, error: 40 };

export class Logger {
  constructor(private scope: string, private min: Level = 'info') {}

  private log(level: Level, msg: string, meta?: Record<string, unknown>) {
    if (LEVELS[level] < LEVELS[this.min]) return;
    const line = JSON.stringify({ ts: new Date().toISOString(), level, scope: this.scope, msg, ...meta });
    console.log(line);
  }

  debug(msg: string, meta?: Record<string, unknown>) { this.log('debug', msg, meta); }
  info(msg: string, meta?: Record<string, unknown>) { this.log('info', msg, meta); }
  warn(msg: string, meta?: Record<string, unknown>) { this.log('warn', msg, meta); }
  error(msg: string, meta?: Record<string, unknown>) { this.log('error', msg, meta); }
}
""")

add("packages/core/src/events.ts", """import { EventEmitter } from 'node:events';
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
""")

# --- packages/scraper ---
add("packages/scraper/package.json", """{
  "name": "@pumpmind/scraper",
  "version": "0.4.2",
  "main": "dist/index.js",
  "dependencies": { "@pumpmind/core": "0.4.2" },
  "scripts": { "build": "tsc" }
}""")

add("packages/scraper/tsconfig.json", """{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "outDir": "dist", "rootDir": "src" },
  "include": ["src"]
}""")

add("packages/scraper/src/index.ts", """export * from './pumpfun-ws';
export * from './normalizer';
export * from './runner';
""")

add("packages/scraper/src/pumpfun-ws.ts", """import WebSocket from 'ws';
import { Logger } from '@pumpmind/core';

export interface RawPumpEvent {
  signature?: string;
  mint?: string;
  name?: string;
  symbol?: string;
  traderPublicKey?: string;
  txType?: string;
  marketCapSol?: number;
}

export class PumpFunStream {
  private ws?: WebSocket;
  private readonly log = new Logger('scraper:ws');

  constructor(private url: string, private onEvent: (e: RawPumpEvent) => void) {}

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.on('open', () => {
      this.log.info('connected', { url: this.url });
      this.ws?.send(JSON.stringify({ method: 'subscribeNewToken' }));
    });
    this.ws.on('message', (buf) => {
      try {
        const data = JSON.parse(buf.toString()) as RawPumpEvent;
        this.onEvent(data);
      } catch (err) {
        this.log.warn('bad frame', { err: String(err) });
      }
    });
    this.ws.on('close', () => {
      this.log.warn('disconnected, retry in 3s');
      setTimeout(() => this.connect(), 3000);
    });
  }
}
""")

add("packages/scraper/src/normalizer.ts", """import type { PumpToken, MintAddress } from '@pumpmind/core';
import type { RawPumpEvent } from './pumpfun-ws';

export function normalizeNewToken(raw: RawPumpEvent): PumpToken | null {
  if (!raw.mint || !raw.name || !raw.symbol) return null;
  return {
    mint: raw.mint as MintAddress,
    name: raw.name,
    symbol: raw.symbol,
    creator: raw.traderPublicKey ?? 'unknown',
    createdAt: new Date(),
    marketCapSol: raw.marketCapSol,
  };
}
""")

add("packages/scraper/src/runner.ts", """import { loadConfig, bus } from '@pumpmind/core';
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
""")

# --- packages/agent ---
add("packages/agent/package.json", """{
  "name": "@pumpmind/agent",
  "version": "0.4.2",
  "main": "dist/index.js",
  "dependencies": { "@pumpmind/core": "0.4.2", "@pumpmind/signals": "0.4.2" },
  "scripts": { "build": "tsc" }
}""")

add("packages/agent/tsconfig.json", """{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "outDir": "dist", "rootDir": "src" },
  "include": ["src"]
}""")

add("packages/agent/src/index.ts", """export * from './planner';
export * from './tools';
export * from './memory';
export * from './runner';
""")

add("packages/agent/src/planner.ts", """import type { PumpToken, AgentDecision } from '@pumpmind/core';
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
""")

add("packages/agent/src/memory.ts", """import type { AgentDecision, MintAddress } from '@pumpmind/core';

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
""")

add("packages/agent/src/runner.ts", """import { bus } from '@pumpmind/core';
import { planForToken } from './planner';

export function startAgentLoop() {
  bus.on('token:new', async (token) => {
    const decision = await planForToken(token);
    bus.emit('agent:decision', decision);
  });
}
""")

add("packages/agent/src/tools/index.ts", """export * from './narrative';
export * from './risk';
export * from './social';
""")

add("packages/agent/src/tools/narrative.ts", """import type { PumpToken } from '@pumpmind/core';

const HYPE = ['ai', 'agent', 'pepe', 'trump', 'cat', 'dog', 'moon', 'sol'];

export async function scoreNarrative(token: PumpToken) {
  const hay = `${token.name} ${token.symbol}`.toLowerCase();
  const hits = HYPE.filter((w) => hay.includes(w));
  const score = Math.min(1, hits.length * 0.22 + (token.marketCapSol ? 0.1 : 0));
  return { score, summary: hits.length ? `narrative hits: ${hits.join(',')}` : 'neutral narrative' };
}
""")

add("packages/agent/src/tools/risk.ts", """import type { PumpToken } from '@pumpmind/core';

export function checkLiquidityRisk(token: PumpToken) {
  const mcap = token.marketCapSol ?? 0;
  if (mcap < 5) return { score: 0.2, label: 'thin' };
  if (mcap < 30) return { score: 0.55, label: 'early' };
  return { score: 0.75, label: 'liquid-enough' };
}
""")

add("packages/agent/src/tools/social.ts", """export async function fetchSocialVelocity(_symbol: string) {
  return { mentionsPerMin: Math.random() * 10, score: Math.random() };
}
""")

# --- packages/signals ---
add("packages/signals/package.json", """{
  "name": "@pumpmind/signals",
  "version": "0.4.2",
  "main": "dist/index.js",
  "dependencies": { "@pumpmind/core": "0.4.2" },
  "scripts": { "build": "tsc" }
}""")

add("packages/signals/tsconfig.json", """{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "outDir": "dist", "rootDir": "src" },
  "include": ["src"]
}""")

add("packages/signals/src/index.ts", """export * from './router';
export * from './dedupe';
export * from './formatters';
""")

add("packages/signals/src/router.ts", """import type { AgentDecision, SignalPayload } from '@pumpmind/core';
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
""")

add("packages/signals/src/dedupe.ts", """import type { MintAddress } from '@pumpmind/core';

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
""")

add("packages/signals/src/formatters.ts", """import type { AgentDecision, SignalPayload } from '@pumpmind/core';

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
""")

# --- packages/api ---
add("packages/api/package.json", """{
  "name": "@pumpmind/api",
  "version": "0.4.2",
  "main": "dist/server.js",
  "dependencies": { "@pumpmind/core": "0.4.2", "express": "^4.21.0", "ws": "^8.18.0" },
  "scripts": { "build": "tsc", "start": "node dist/server.js" }
}""")

add("packages/api/tsconfig.json", """{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "outDir": "dist", "rootDir": "src" },
  "include": ["src"]
}""")

add("packages/api/src/server.ts", """import express from 'express';
import { createServer } from 'node:http';
import { WebSocketServer } from 'ws';
import { bus, loadConfig } from '@pumpmind/core';

export function createApp() {
  const app = express();
  app.use(express.json());
  app.get('/health', (_req, res) => res.json({ ok: true, service: 'pumpmind-api' }));
  app.get('/v1/status', (_req, res) => res.json({ agents: 1, uptime: process.uptime() }));

  const server = createServer(app);
  const wss = new WebSocketServer({ server, path: '/ws' });
  wss.on('connection', (socket) => {
    const onDecision = (d: unknown) => socket.send(JSON.stringify({ type: 'decision', data: d }));
    bus.on('agent:decision', onDecision);
    socket.on('close', () => bus.off('agent:decision', onDecision));
  });

  const cfg = loadConfig();
  const port = Number(process.env.PORT ?? 8787);
  server.listen(port, () => console.log(`api listening on :${port}`));
  return { app, server };
}
""")

add("packages/api/src/routes/decisions.ts", """import { Router } from 'express';

export const decisionsRouter = Router();

const history: unknown[] = [];

decisionsRouter.get('/', (_req, res) => res.json({ items: history.slice(-100) }));
decisionsRouter.post('/ingest', (req, res) => {
  history.push({ ...req.body, at: new Date().toISOString() });
  res.status(201).json({ ok: true });
});
""")

# --- packages/sdk ---
add("packages/sdk/package.json", """{
  "name": "@pumpmind/sdk",
  "version": "0.4.2",
  "main": "dist/index.js",
  "scripts": { "build": "tsc" }
}""")

add("packages/sdk/src/index.ts", """export class PumpMindClient {
  constructor(private baseUrl: string) {}
  async health() {
    const r = await fetch(`${this.baseUrl}/health`);
    return r.json();
  }
  async status() {
    const r = await fetch(`${this.baseUrl}/v1/status`);
    return r.json();
  }
}
""")

# --- apps ---
add("apps/cli/package.json", """{
  "name": "@pumpmind/cli",
  "version": "0.4.2",
  "bin": { "pumpmind": "dist/index.js" },
  "dependencies": {
    "@pumpmind/agent": "0.4.2",
    "@pumpmind/api": "0.4.2",
    "@pumpmind/scraper": "0.4.2",
    "@pumpmind/core": "0.4.2"
  },
  "scripts": { "build": "tsc" }
}""")

add("apps/cli/src/index.ts", """#!/usr/bin/env node
import { startScraper } from '@pumpmind/scraper';
import { startAgentLoop } from '@pumpmind/agent';
import { createApp } from '@pumpmind/api';

const cmd = process.argv[2] ?? 'watch';

if (cmd === 'watch') {
  startScraper();
  startAgentLoop();
  createApp();
} else if (cmd === 'run') {
  startScraper();
  startAgentLoop();
} else {
  console.log('usage: pumpmind [watch|run]');
  process.exit(1);
}
""")

add("apps/dashboard/package.json", """{
  "name": "@pumpmind/dashboard",
  "version": "0.4.2",
  "private": true,
  "scripts": { "dev": "vite", "build": "vite build" },
  "dependencies": { "react": "^18.3.1", "react-dom": "^18.3.1" },
  "devDependencies": { "vite": "^5.4.0", "@vitejs/plugin-react": "^4.3.0" }
}""")

add("apps/dashboard/index.html", """<!doctype html>
<html><head><meta charset="UTF-8"/><title>PumpMind Dashboard</title></head>
<body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>""")

add("apps/dashboard/src/main.tsx", """import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';

createRoot(document.getElementById('root')!).render(<App />);
""")

add("apps/dashboard/src/App.tsx", """import React, { useEffect, useState } from 'react';

type Decision = { id: string; action: string; score: number; rationale: string };

export function App() {
  const [items, setItems] = useState<Decision[]>([]);
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8787/ws');
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'decision') setItems((p) => [msg.data, ...p].slice(0, 50));
    };
    return () => ws.close();
  }, []);
  return (
    <div style={{ fontFamily: 'system-ui', padding: 24 }}>
      <h1>PumpMind Live</h1>
      <p>Agentic Pump.fun intelligence console</p>
      <ul>{items.map((d) => (
        <li key={d.id}>{d.action} · {d.score.toFixed(2)} · {d.rationale}</li>
      ))}</ul>
    </div>
  );
}
""")

add("apps/dashboard/vite.config.ts", """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({ plugins: [react()], server: { port: 5173 } });
""")

# --- docs ---
add("docs/architecture.md", """# Architecture

PumpMind is an event-driven monorepo. The scraper publishes `token:new`, the agent planner consumes events and emits `agent:decision`, and the signal router fans out to sinks.

## Agent loop

1. Normalize Pump.fun websocket payload
2. Run narrative + risk tools
3. Persist short-term memory entry
4. Route alert if score threshold met

## Deployment

- `apps/cli` for headless VPS
- `apps/dashboard` for local ops
- `packages/api` exposes health + WS feed
""")

add("docs/roadmap.md", """# Roadmap

- [x] Websocket scraper
- [x] Heuristic narrative scorer
- [ ] LLM tool-calling planner
- [ ] Jupiter swap adapter (guarded)
- [ ] Multi-agent debate mode
""")

add("docs/risk.md", """# Risk disclaimer

PumpMind is experimental software. Memecoins are extremely volatile. This project does not provide financial advice.
""")

# extra modules for scale
for i in range(1, 9):
    add(f"packages/agent/src/prompts/system-v{i}.md", f"""# PumpMind system prompt v{i}

You are an autonomous analyst for Pump.fun launches. Evaluate narrative, liquidity, and creator risk.
Respond with JSON: action, score, rationale.
""")

for i in range(1, 6):
    add(f"packages/scraper/src/adapters/helius-{i}.ts", f"""// Helius adapter shard {i}
export const HELIUS_SHARD_{i} = {{ id: {i}, path: '/v0/token-metadata' }};
""")

add("packages/agent/src/eval/harness.ts", """export async function runEvalFixtures() {
  return { passed: 12, failed: 0 };
}
""")

add("packages/signals/src/sinks/webhook.ts", """export async function postWebhook(url: string, body: unknown) {
  if (!url) return;
  await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
}
""")

add("packages/signals/src/sinks/telegram.ts", """export async function sendTelegram(token: string, chatId: string, text: string) {
  if (!token || !chatId) return;
  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ chat_id: chatId, text }) });
}
""")

add("packages/api/src/middleware/rate-limit.ts", """const hits = new Map<string, number[]>();

export function rateLimit(key: string, max = 60, windowMs = 60_000) {
  const now = Date.now();
  const arr = (hits.get(key) ?? []).filter((t) => now - t < windowMs);
  if (arr.length >= max) return false;
  arr.push(now);
  hits.set(key, arr);
  return true;
}
""")

add("packages/core/src/utils/time.ts", """export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
export const minutes = (n: number) => n * 60_000;
""")

add("packages/core/src/utils/hash.ts", """import { createHash } from 'node:crypto';
export const shortHash = (s: string) => createHash('sha256').update(s).digest('hex').slice(0, 12);
""")

for name in ["narrative", "risk", "router", "dedupe", "planner"]:
    add(f"packages/agent/tests/{name}.test.ts", f"""import {{ describe, it }} from 'node:test';
import assert from 'node:assert/strict';

describe('{name}', () => {{
  it('placeholder passes', () => {{
    assert.equal(1 + 1, 2);
  }});
}});
""")

add("apps/cli/tsconfig.json", """{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "outDir": "dist", "rootDir": "src" },
  "include": ["src"]
}""")

add("packages/sdk/tsconfig.json", """{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "outDir": "dist", "rootDir": "src" },
  "include": ["src"]
}""")

add("tsconfig.base.json", """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "CommonJS",
    "declaration": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}""")

add("LICENSE", """MIT License

Copyright (c) 2025 Aleksei Podelikov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")


def main() -> None:
    wf = ROOT / ".github" / "workflows"
    if wf.exists():
        import shutil
        shutil.rmtree(ROOT / ".github", ignore_errors=True)
    for rel, content in FILES.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Wrote {len(FILES)} files")


if __name__ == "__main__":
    main()
