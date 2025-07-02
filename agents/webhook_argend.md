# Webhook Agent

## Purpose
Sends messages and files via Discord webhooks or channels.

## Environment Variables
- `DISCORD_WEBHOOK_URL` – default webhook URL (optional)
- `EVENT_CHANNEL_ID` – Discord channel ID for event messages (optional)

## External Dependencies
- Requests library
- `utils.discord_util.send_discord_message`
