#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import { runSync } from '../lib/sync.js';
import { runAudit } from '../lib/audit.js';
import { runRelease } from '../lib/release.js';

const program = new Command();
program
  .name('codex-fur')
  .description('FUR Codex CLI – Audits, i18n-Sync, Release & Auto-Fixes')
  .version('1.0.0');

program.command('sync').description('Synchronisiere i18n').action(runSync);
program.command('audit').description('Codex-Audit ausführen').action(runAudit);
program.command('release').description('Release mit Auto-Push').action(runRelease);

program.parse();