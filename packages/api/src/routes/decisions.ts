import { Router } from 'express';

export const decisionsRouter = Router();

const history: unknown[] = [];

decisionsRouter.get('/', (_req, res) => res.json({ items: history.slice(-100) }));
decisionsRouter.post('/ingest', (req, res) => {
  history.push({ ...req.body, at: new Date().toISOString() });
  res.status(201).json({ ok: true });
});
