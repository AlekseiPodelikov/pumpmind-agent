export class PumpMindClient {
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
