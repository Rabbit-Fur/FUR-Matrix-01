

Willkommen im Kernsystem von **FUR (Federated Utility Rabbit)** – einem modularen Discord-, Kalender- und Ereignis-Managementsystem mit GPT-gestütztem Multi-Agent-Netzwerk, MongoDB, Google-API-Integration und vollautomatisierten Abläufen.

> Dieses Repository folgt dem Codex-Protokoll QUM-1.0 und ist vollständig kompatibel mit Codex-Aktionen, Commit-Governance und Agenten-Routing.

---

## 🚀 Quickstart

# 1. Repository klonen

git clone https://github.com/Rabbit-Fur/try.git
cd try

# 2. Umgebung konfigurieren

cp .env.example .env
# 3. Pre-commit installieren

pre-commit install

# 4. Starten (lokal)

poetry run python main_app.py

🧱 Struktur

.
├── agents/                # Alle Codex-konformen Agenten
├── bot/                   # Discord-Bot + Cogs
├── blueprints/           # Flask-API (OAuth, User, Events)
├── db/                   # MongoDB-Logik, Zugriffsschicht
├── tests/                # pytest-Tests
├── .copilot/             # Codex-Regeln, Commit- und Branchrichtlinien
├── argend.md             # Agent-Beschreibung (optional pro Modul)
└── AGENTS.md             # Übersicht aller registrierten Agenten
⚙️ Konfiguration

Erstelle .env basierend auf .env.example:

env
DISCORD_TOKEN=...
GOOGLE_CLIENT_SECRET=...
MONGO_URI=mongodb+srv://...
OPENAI_API_KEY=...
GITHUB_TOKEN=...
DEBUG=true

`GITHUB_TOKEN` wird für Zugriffe auf die GitHub API benötigt.
Weitere Details zu allen Variablen finden sich in [docs/env_vars.md](docs/env_vars.md).

### Discord OAuth `.env` Variablen

Für den Discord-Login müssen folgende Variablen in `.env` gesetzt werden:

- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `DISCORD_REDIRECT_URI`
- `DISCORD_GUILD_ID`
- `DISCORD_TOKEN`
- `R3_ROLE_IDS`, `R4_ROLE_IDS`, `ADMIN_ROLE_IDS`

### Login- und Callback-Flow

1. Nutzer ruft `/login/discord` auf und wird zu Discord weitergeleitet.
2. Discord fragt Berechtigungen für die Scopes `identify`, `guilds` und `guilds.members.read` an.
3. Nach Zustimmung leitet Discord zur in `DISCORD_REDIRECT_URI` konfigurierten URL (z. B. `/callback`) zurück und übergibt `code` und `state`.
4. Die Anwendung validiert `state` und tauscht `code` mithilfe von `DISCORD_CLIENT_ID` und `DISCORD_CLIENT_SECRET` gegen ein Access Token.
5. Mit diesem Token werden `/users/@me` sowie `/users/@me/guilds/{DISCORD_GUILD_ID}/member` abgefragt.
6. Die Discord-Rollen werden mit `R3_ROLE_IDS`, `R4_ROLE_IDS` und `ADMIN_ROLE_IDS` verglichen; nur passende Rollen erhalten Zugriff.
7. Abhängig vom Rollenlevel erfolgt die Weiterleitung zum Admin- oder Member-Dashboard.

📡 Features

✅ Zwei-Wege-Kalendersync (Google ↔ MongoDB)

✅ Vollständig modularisiertes Agentensystem

✅ Discord-Bot mit intelligenten Cogs (/cal, /now, /add)

🧠 Kontextspeicher für Multi-User-Prompting

📁 Logging + Event-Trail über log_agent

🌐 Externe Webhook-Verarbeitung (z. B. GitHub, Stripe)

📦 Agenten (Auszug)

Agent	Zweck

reminder_agent	Erinnerungen via Kalender / Discord
auth_agent	Auth mit Discord, Google OAuth
scheduler_agent	Zeitbasierte Planung & Trigger
poster_agent	Bildgenerierung über image_api
tagging_agent	Automatische Kategorisierung

→ Vollständige Liste: AGENTS.md

📜 Codex-Protokoll (QUM-1.0)

Jeder Agent benötigt eine eigene argend.md

Commit Messages folgen dem Schema COD:agent-name → kurzbeschreibung

Commit-Lint, Branch- und PR-Regeln werden über .copilot/config.json gesteuert

Jeder Branch beginnt mit feature/, fix/, agent/, release/

🧪 Tests

pytest tests/

Testabdeckung für Agenten, API-Flows, Discord-Kommandos

Linting: ruff, mypy, black

Pre-Commit Hooks aktiviert (.pre-commit-config.yaml)
Vor dem ersten Commit: `pre-commit install`

📄 Dokumentation

Agentendefinitionen: AGENTS.md

API-Flows: docs/oauth.md

MongoDB Setup: docs/mongo.md

🔐 Sicherheit

Alle Secrets sind über .env geschützt

Token Refresh-Flows sind implementiert

Codex blockiert Deployment ohne .env.example + Commit-Lint

## Google Calendar → Eventbild → Discord Workflow

- Liest Events automatisiert aus Google Calendar
- Erstellt für jedes Event ein ansprechendes Eventbild (FUR-Style)
- Postet Event + Bild als Embed ins Discord (mit `!postevent`)
- Vollständig modular, robust und testbar umgesetzt
- Für Setup siehe `requirements.txt` und API-Doku im Ordner `docs/`

### APScheduler Calendar Sync Example

Schedule periodic synchronisation by creating a `CalendarService` within a
Flask application context. The job interval is driven by the
``GOOGLE_SYNC_INTERVAL_MINUTES`` configuration (default ``30`` minutes). OAuth
tokens are loaded from the path specified via ``GOOGLE_TOKEN_STORAGE_PATH`` or
``GOOGLE_CREDENTIALS_FILE``.

```python
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio, os
from services import CalendarService
from web import create_app

app = create_app()
scheduler = BackgroundScheduler()

def sync_calendar():
    with app.app_context():
        service = CalendarService()
        asyncio.run(service.sync())

scheduler.add_job(
    sync_calendar,
    "interval",
    minutes=int(os.getenv("GOOGLE_SYNC_INTERVAL_MINUTES", "30")),
)
scheduler.start()
```

📬 Kontakt

Maintainer: Marcel Schlanzke

Discord: see_u_m

🛠️ Kompatibilität

Komponente	Version
Python	3.11.x
MongoDB Atlas	≥ 5.0
Discord.py	2.x
Google API	v3
OpenAI API	GPT-4 Turbo

📜 Lizenz
MIT – siehe LICENSE


