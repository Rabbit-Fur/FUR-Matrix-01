#!/usr/bin/env bash
set -euo pipefail

if ! command -v codex >/dev/null 2>&1; then
  echo "Installing Codex CLI via npm..."
  npm i -g @openai/codex
fi

echo "Codex version:"
codex --version

echo "If you haven't logged in yet, run: codex login"
echo "To start the agent: make codex  # or simply 'codex'"
