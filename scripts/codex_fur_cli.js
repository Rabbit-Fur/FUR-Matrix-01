// codex_fur_cli_extended.js – erweitert mit universal-init
import { Command } from 'commander';
import chalk from 'chalk';
import { runSync } from '../lib/sync.js';
import { runAudit } from '../lib/audit.js';
import { runRelease } from '../lib/release.js';
import { execSync } from 'child_process';

const program = new Command();

program
  .name('codex-fur')
  .description('FUR Codex CLI – Audits, i18n-Sync, Release & Universal Runtime Init')
  .version('1.1.0');

program
  .command('sync')
  .description('Synchronisiere alle i18n-Dateien im Projekt')
  .action(runSync);

program
  .command('audit')
  .description('Führe Codex-Prüfung & Auto-Fix durch')
  .action(runAudit);

program
  .command('release')
  .description('Führe Release auf main durch inkl. Codex-Push & Tag')
  .action(runRelease);

program
  .command('universal-init')
  .description('Starte den Codex Universal Runtime Environment Check')
  .action(() => {
    try {
      console.log(chalk.cyan('🧠 Initialisiere Codex Universal Umgebung...'));
      execSync('python3 core/universal/setup.py', { stdio: 'inherit' });
    } catch (err) {
      console.error(chalk.red('❌ Fehler beim Initialisieren der Umgebung:'), err);
    }
  });

program.parse();
