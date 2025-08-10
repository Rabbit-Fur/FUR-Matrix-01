# 🤖 Codex – Integration Pack

Dieses Pack integriert den OpenAI Codex CLI Agent in dein Repo **Rabbit-Fur/try**.

## Schnellstart (lokal)
```bash
npm i -g @openai/codex
codex login   # oder OPENAI_API_KEY setzen
codex
```

## Repro via Docker
```bash
docker compose -f docker-compose.codex.yml up -d
docker compose -f docker-compose.codex.yml exec codex-dev bash
codex
```

## CI (GitHub Actions)
1) Setze **OPENAI_API_KEY** als Repository Secret.
2) Push/PR triggert `.github/workflows/codex-ci.yml`.

## Konfiguration
- Agent-Policy: `AGENTS.md`
- Repo-Config: `codex.config.toml`
- Aufgaben: `codex.tasks.yaml`
- Make Targets: `make codex`, `make codex-fix`
- Basis-URL: `https://fur-martix.up.railway.app/` (aus deiner `.env`)

## Hinweise
- Keine Secrets committen — `.env.example` nutzen und echte Werte via Secrets/ENV bereitstellen.
- Toolchain-Versionen:
  - Python 3.11.12, Node 20, Rust 1.87.0, Go 1.23.8, Swift 6.1
