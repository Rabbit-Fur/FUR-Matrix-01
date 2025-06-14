#!/bin/bash

echo "🚀 Initialisiere Codex FUR Setup ..."

# 1. package.json vorbereiten (einfügen oder updaten)
echo "📦 Erstelle/aktualisiere package.json..."

cat <<EOF > package.json
{
  "name": "fur-codex",
  "version": "1.0.0",
  "description": "FUR Codex Automatisierung",
  "scripts": {
    "codex:audit": "npx openai codex audit",
    "codex:fix": "npx openai codex fix",
    "codex:release": "npx openai codex release"
  },
  "devDependencies": {}
}
EOF

# 2. .codexrc.json anlegen
echo "🧠 Erstelle .codexrc.json..."

cat <<EOF > .codexrc.json
{
  "projectName": "FUR-System",
  "include": ["main/**/*.py", "web/**/*.py", "bot/**/*.py", "main/translations/*.json"],
  "exclude": ["**/migrations/**", "**/__pycache__/**"],
  "rules": {
    "python": {
      "style": "pep8",
      "docstrings": true,
      "translations": true
    }
  }
}
EOF

# 3. GitHub Action hinzufügen
echo "⚙️  Erstelle GitHub Workflow..."

mkdir -p .github/workflows

cat <<EOF > .github/workflows/codex-fur.yml
name: Codex FUR Release

on:
  workflow_dispatch:
  push:
    paths:
      - ".codexrc.json"
      - "main/translations/**"
      - "web/**"
      - "bot/**"
    branches:
      - main

jobs:
  codex:
    name: Run Codex Tasks
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 20

      - name: Install dependencies
        run: npm install

      - name: Run Codex Audit
        run: npm run codex:audit

      - name: Run Codex Fix
        run: npm run codex:fix

      - name: Run Codex Release
        run: npm run codex:release
EOF

# 4. Husky installieren + Hook einrichten
echo "🪝 Installiere Husky & pre-commit Hook..."

npx husky install
npx husky add .husky/pre-commit "npm run codex:audit && npm run codex:fix"

# 5. Fertig
echo "✅ Codex Setup abgeschlossen! Du kannst jetzt starten mit:"
echo "   👉  npm run codex:audit"
echo "   👉  npm run codex:fix"
echo "   👉  npm run codex:release"
