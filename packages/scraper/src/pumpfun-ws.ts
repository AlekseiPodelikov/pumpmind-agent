import WebSocket from 'ws';
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

// 2025-07-23
