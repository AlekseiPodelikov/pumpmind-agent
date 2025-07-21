import { readFileSync, existsSync } from 'node:fs';
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
    for (const line of readFileSync(envPath, 'utf8').split('\n')) {
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
