type Level = 'debug' | 'info' | 'warn' | 'error';

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
