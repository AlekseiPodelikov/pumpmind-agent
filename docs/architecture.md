# Architecture

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
