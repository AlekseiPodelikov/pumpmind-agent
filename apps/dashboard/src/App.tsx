import React, { useEffect, useState } from 'react';

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
