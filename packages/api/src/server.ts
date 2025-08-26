import express from 'express';
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

// 2025-07-25

// 2025-08-26
