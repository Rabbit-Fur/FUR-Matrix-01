# FUR SYSTEM

Dieses Projekt beinhaltet ein vollständig integriertes Event-, Champion- und Reminder-System für Grand Gangster War – entwickelt für die FUR-Allianz.

## Module
- Flask-Webportal mit Authentifizierung (Discord OAuth)
- Discord-Bot mit modularen Cogs (Reminder, Champion, Leaderboard)
- Codex-AutoFix & i18n-Tooling (codex-fur CLI)
- Champion-Autopilot mit Poster-Generierung & Webhook-Versand

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main_app.py
```

## CLI
```bash
codex-fur sync     # Übersetzungen synchronisieren
codex-fur audit    # Projekt analysieren & fixen
codex-fur release  # Commit, Push & Tag auf main
```