#!/bin/bash

# 🚀 FUR SYSTEM – GitHub Secrets Setup Script
# Projekt: Rabbit-Fur/try
# Erstellt für Codex-Umgebungen und manuelle Secret-Initialisierung
# Version: QUM-1.0

REPO="Rabbit-Fur/try"

secrets=(
  REPO_GITHUB
  FUR_PAT
  TOKEN_GITHUB_API
  DISCORD_TOKEN
  DISCORD_CLIENT_ID
  DISCORD_CLIENT_SECRET
  DISCORD_GUILD_ID
  public_CHANNEL_ID
  EVENT_CHANNEL_ID
  REMINDER_CHANNEL_ID
  LEADERBOARD_CHANNEL_ID
  HoF_CHANNEL_ID
  R3_ROLE_IDS
  R4_ROLE_IDS
  ADMIN_ROLE_IDS
  DISCORD_WEBHOOK_URL
  DISCORD_REDIRECT_URI
  GOOGLE_CLIENT_ID
  GOOGLE_PROJECT_ID
  GOOGLE_CLIENT_SECRET
  GOOGLE_AUTH_URI
  GOOGLE_TOKEN_URI
  GOOGLE_AUTH_PROVIDER_CERT_URL
  GOOGLE_REDIRECT_URI
  ENABLE_DISCORD_BOT
  OPENAI_API_KEY
  PORT
  BASE_URL
  FLASK_ENV
  SECRET_KEY
  SESSION_LIFETIME_MINUTES
  DATABASE_URL
  LOGTAIL_TOKEN
)

echo "🧠 Starte Codex-kompatibles Setup für: $REPO"

for key in "${secrets[@]}"; do
  value="${!key}"
  if [ -n "$value" ]; then
    echo "🔐 Setze Secret: $key"
    gh secret set "$key" -b "$value" -R "$REPO"
  else
    echo "⚠️ $key nicht gesetzt, überspringe"
  fi
done

echo "✅ Setup abgeschlossen. Alle Secrets wurden gesetzt, sofern vorhanden."
