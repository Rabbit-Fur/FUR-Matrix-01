import chalk from 'chalk';
import { execSync } from 'child_process';

export async function runRelease() {
  console.log(chalk.cyan('🚀 Starte Codex-Release auf main...'));

  try {
    execSync('git add .', { stdio: 'inherit' });
    execSync('git commit -m "🔁 Codex-AutoRelease"', { stdio: 'inherit' });
    execSync('git push origin main', { stdio: 'inherit' });

    const tag = `codex-v${new Date().toISOString().slice(0, 10)}`;
    execSync(`git tag ${tag}`, { stdio: 'inherit' });
    execSync(`git push origin ${tag}`, { stdio: 'inherit' });

    console.log(chalk.green('✅ Release abgeschlossen.'));
  } catch (err) {
    console.error(chalk.red('❌ Fehler beim Release:'), err);
  }
}