#!/usr/bin/env node
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
