# MATRIX / FUR — Codex Leitplanken

## Mission
- Codex arbeitet **nur** an diesem Repo und respektiert den FUR‑Codex (Linting, Tests, Branches, Commits, Security).
- Prioritäten: **Stabilität > Korrektheit > Lesbarkeit > Performance**.

## Stack & Versionen
- Python: 3.11.12
- Node: 20
- Rust: 1.87.0
- Go: 1.23.8
- Swift: 6.1
- Flask‑Web + Discord Bot (Cogs) + MongoDB + Google Calendar Sync

## Architektur-Hinweise
- Web: Flask App Factory, Blueprints, Jinja, i18n (flask_babel_next).
- Bot: discord.py Cogs (`bot/cogs/*`). Long‑running Jobs via asyncio + APScheduler.
- Daten: MongoDB (URI über ENV), SQLite/SQLAlchemy (DATABASE_URL), Logging standardisiert.
- Google Sync: `utils/google_sync_task.py` + `blueprints/google_auth.py`, Token/Client‑Files via ENV‑Pfad.

## Coding-Standards
- **Commits**: Conventional Commits (`feat|fix|chore|docs|test|refactor|ci(scope): msg`).
- **Branching**: `main` (stabil), `dev` (integration), Feature‑Branches `feat/*`.
- **Python**: ruff + black, pytest mit Coverage ≥ 85 %.
- **JS/TS**: eslint + prettier, vitest/jest wenn sinnvoll.
- **Security**: Nie Secrets committen; nur ENV/GitHub Secrets/Railway Vars.

## Qualitäts-Checks (die Codex automatisch ausführt)
1. Lint/Format Fixes (safe edits).
2. Tests generieren/auffüllen, Ziel: 85 %+ Coverage.
3. README/Doku‑Updates und `CHANGELOG.md`.
4. PR‑Beschreibung & Checkliste schreiben.

## Wichtige Aufgaben für Codex (Beispiele)
- **Flask Context Fix**: Fehler „Working outside of application context“ in `bot.cogs.calendar_cog` beheben (AppContext sauber injizieren).
- **Google OAuth/Sync**: Token‑Flow robust machen, Fehlerbehandlung + Logs, Mongo‑Persistenz.
- **i18n Harmonisierung**: Alle Sprach‑JSONs key‑identisch halten, Tooling für Missing‑Keys.
- **Discord Media**: Grafikerstellung → Versand (Filesize‑Limit, Async‑I/O, Retry‑Policy).

## Reviews & Tests
- Vor Merge: `pytest -q`, Lint grün, PR checkt Secrets‑Leaks (pre‑commit).
- Merges nur via PR mit grünem CI.

---

# Rust/codex-rs

In the codex-rs folder where the rust code lives:

- Never add or modify any code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR`.
  - You operate in a sandbox where `CODEX_SANDBOX_NETWORK_DISABLED=1` will be set whenever you use the `shell` tool. Any existing code that uses `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` was authored with this fact in mind. It is often used to early exit out of tests that the author knew you would not be able to run given your sandbox limitations.
  - Similarly, when you spawn a process using Seatbelt (`/usr/bin/sandbox-exec`), `CODEX_SANDBOX=seatbelt` will be set on the child process. Integration tests that want to run Seatbelt themselves cannot be run under Seatbelt, so checks for `CODEX_SANDBOX=seatbelt` are also often used to early exit out of tests, as appropriate.

Before creating a pull request with changes to `codex-rs`, run `just fmt` (in `codex-rs` directory) to format the code and `just fix` (in `codex-rs` directory) to fix any linter issues in the code, ensure the test suite passes by running `cargo test --all-features` in the `codex-rs` directory.

When making individual changes prefer running tests on individual files or projects first.
