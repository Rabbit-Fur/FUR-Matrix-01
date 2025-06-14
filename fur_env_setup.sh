#!/bin/bash

# 🚀 FUR SYSTEM – GitHub Secrets Setup Script
# Projekt: Rabbit-Fur/try
# Erstellt für Codex-Umgebungen und manuelle Secret-Initialisierung
# Version: QUM-1.0

REPO="Rabbit-Fur/try"

# GitHub Token
FUR_PAT="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"
TOKEN_GITHUB_API="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"

declare -A secrets=(
  # GitHub
  ["FUR_PAT"]="$FUR_PAT"
  ["TOKEN_GITHUB_API"]="$TOKEN_GITHUB_API"

  # Discord
  ["DISCORD_TOKEN"]="MTM2Mjg4ODY4ODk5MTczMTk2Mw.GT4mAi.pZDNFRO2lxJjxhYcaC-386nqwxi_PpT6VZZv6o"
  ["DISCORD_CLIENT_ID"]="1362888688991731963"
  ["DISCORD_CLIENT_SECRET"]="huzQ64HW4ESlayAV0J1VzfazUlTIB7CX"
  ["DISCORD_GUILD_ID"]="1344968805151019088"
  ["public_CHANNEL_ID"]="1344996126444748810"
  ["EVENT_CHANNEL_ID"]="1365580225945014385"
  ["REMINDER_CHANNEL_ID"]="1383478113547325450"
  ["LEADERBOARD_CHANNEL_ID"]="1383476164252926042"
  ["HoF_CHANNEL_ID"]="1383476281236127744"
  ["R3_ROLE_IDS"]="123456789012345678"
  ["R4_ROLE_IDS"]="234567890123456789"
  ["ADMIN_ROLE_IDS"]="345678901234567890"
  ["DISCORD_WEBHOOK_URL"]="https://discord.com/api/webhooks/1361477364457930923/CVK_3Ri2m1qDHf7Fvg5tg0wlhb5Qs9G1T6fhvFPFgemmJM4my1RdUm7kRuSanK7P9wva"
  ["DISCORD_REDIRECT_URI"]="https://fur-martix.up.railway.app/callback"

  # Google
  ["GOOGLE_CLIENT_ID"]="858610490497-6l1rp8bo51e7sd3pmklhpmbcrf9bfbft.apps.googleusercontent.com"
  ["GOOGLE_PROJECT_ID"]="erudite-fusion-456918-h4"
  ["GOOGLE_CLIENT_SECRET"]="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"
  ["GOOGLE_AUTH_URI"]="https://accounts.google.com/o/oauth2/auth"
  ["GOOGLE_TOKEN_URI"]="https://oauth2.googleapis.com/token"
  ["GOOGLE_AUTH_PROVIDER_CERT_URL"]="https://www.googleapis.com/v1/certs"
  ["GOOGLE_REDIRECT_URI"]="https://fur-martix.up.railway.app/callback/google"

  # FUR System Core
  ["ENABLE_DISCORD_BOT"]="true"
  ["OPENAI_API_KEY"]="proj_JZB3caGonxdtB4nflofV4dyC"
  ["PORT"]="8080"
  ["BASE_URL"]="https://fur-martix.up.railway.app/"
  ["FLASK_ENV"]="production"
  ["SECRET_KEY"]="4fa028caf6d5c91645e37d8ce1400ec1451285bcceafaa3ccf273fcb3396f913"
  ["SESSION_LIFETIME_MINUTES"]="60"
  ["DATABASE_URL"]="sqlite:///fur.db"

  # Logging
  ["LOGTAIL_TOKEN"]="ZrWJhBk5J4XGZKXSCMgdM8Fb"
)

echo "🧠 Starte Codex-kompatibles Setup für: $REPO"

for key in "${!secrets[@]}"; do
  echo "🔐 Setze Secret: $key"
  gh secret set "$key" -b "${secrets[$key]}" -R "$REPO"
done

echo "✅ Setup abgeschlossen. Alle Secrets wurden gesetzt."
