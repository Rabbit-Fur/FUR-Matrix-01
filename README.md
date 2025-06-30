# 🧠 FUR Codex System – Unified Agent & Calendar Platform

> Ein modulares Fullstack-System zur Koordination, Erinnerung und Automatisierung von Events, Agenten und Nutzern – optimiert für Discord, MongoDB, Google Calendar und internationale Teams.

---

## 🚀 Projektbeschreibung

**FUR Codex** ist ein intelligentes Kontrollsystem zur Organisation und Automatisierung von Event-, Kalender- und Kommunikationsprozessen. Es kombiniert:
- 🔁 automatische Erinnerungen & wöchentliche Zusammenfassungen,
- 🤖 GPT-gestützte Agentensysteme (Poster, Reminder, Inbox, etc.),
- 📅 Google Calendar-Synchronisation mit OAuth 2.0,
- 🧩 modulare Blueprints & Discord-Cogs,
- 🌍 mehrsprachige Oberfläche mit Flaggen-UI & JSON-i18n,
- 📦 MongoDB-Integration für Nutzer-, Event- und Reminderdaten,
- 📊 visuelle Dashboards & Leaderboards für Mitglieder.

Das System ist vollständig testbar (pytest), Docker-fähig und CI/CD-ready via Railway.

---

## 📁 Projektstruktur

try-main/
├── agents/ # GPT-gestützte Agenten (Reminder, Poster, Dialog, etc.)
├── blueprints/ # Flask-Routen (API, Admin, Member, Public)
├── bot/ # Discord-Bot & Cogs (Commands, Newsletter, Kalender)
├── codex/ # Codex CLI, Aufgabenplanung, Sync-Tools
├── core/ # Memory Engine, Universal-Schnittstellen, Logging
├── dashboard/ # CI/CD-YAMLs & wöchentlicher Logger
├── database/ # Initialisierung & MongoDB-Anbindung
├── docs/ # Screenshots & technische Dokumentation
├── i18n_tools/ # Lokale Übersetzungswerkzeuge (autofill, sync, extract)
├── models/ # MongoDB-Modellklassen für Events, Users, etc.
├── schemas/ # Pydantic/Marshmallow-Schemas zur Validierung
├── services/ # Dienste wie calendar_service
├── static/ # Assets, Logos, generierte Poster, Flags
├── templates/ # Jinja2-HTML Templates für Admin, Public, Member
├── tests/ # Umfassende Pytest-Testabdeckung (~45 Module)
├── translations/ # JSON-basierte Sprachdateien (50+ Sprachen)
├── utils/ # Hilfsfunktionen (Timezone, Poster, Google, Discord)
├── web/ # Flask Web-Routen, Sockets, Poster-API
├── main_app.py # App-Initialisierung & Entry Point
├── config.py # Konfiguration & ENV-Ladefunktionen
└── requirements.txt # Python-Abhängigkeiten

yaml
Kopieren
Bearbeiten

---

## ⚙️ Installation & Setup

### Voraussetzungen
- Python 3.10+
- MongoDB Atlas URI (z. B. `mongodb+srv://...`)
- Google Cloud OAuth2 Credentials
- Discord Bot Token mit OAuth & Adminrechten
- Optional: Railway, Docker, Make

### Setup-Schritte

```bash
# 1. Repository klonen
git clone https://github.com/deinuser/fur-codex
cd fur-codex

# 2. Virtuelle Umgebung & Abhängigkeiten
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. ENV-Variablen setzen (.env)
cp .env.example .env
# → Trage hier deine MongoDB URI, Google OAuth & Discord Token ein

# 4. Datenbank vorbereiten
python init_db_core.py

# 5. Lokale Tests ausführen
pytest
Optional:

bash
Kopieren
Bearbeiten
# Deployment via Docker
docker build -t fur-codex .
docker run -p 8000:8000 fur-codex

# Railway Deployment (Procfile vorhanden)
railway up
💡 Hauptfunktionen & Zusammenhänge
Modul	Beschreibung
bot/	Discord Bot mit Reminder-System, Kalender-Integration, Opt-out, Signups
agents/	GPT-Agents wie reminder_agent.py, poster_agent.py, auth_agent.py
google_*.py	OAuth2 Flow, Kalender Sync, Event-Pusher nach MongoDB
web/	Flask Webserver mit SocketIO, Poster-API und Admin-Schnittstellen
core/memory/	Memory Engine zur GPT-Kontextsteuerung
fur_mongo.py	Initiale MongoDB-Verbindung & Standard-Sammlungen
utils/	Tools für Zeitzonen, Google-Tasks, Discord-DMs & Poster-Erzeugung
templates/	Jinja2 Templates inkl. Admin-Panel, Event-Views, Leaderboards

🧪 Testen & Qualitätssicherung
bash
Kopieren
Bearbeiten
# Linting
make lint

# Test Suite (Pytest)
make test
# oder
pytest tests/
Die tests/-Suite deckt über 40 Teilmodule ab, inkl. Discord Cogs, Flask Views, Agents & Google-Sync.

📚 Beispielanwendung (Use Cases)
🕓 Daily Reminder Bot für Discord: tägliche DM mit Aufgaben aus dem Mongo-DB Kalender

🗓 Google Calendar Sync: Events aus GCal werden automatisch abgeglichen

🌐 Mehrsprachige Web-Dashboards: mit Flaggenumschaltung & i18n-JS-Bundle

📩 Poster Agent: erstellt automatisch visuelle Eventposter & sendet sie an Discord-Channels

🧠 Memory Agent: verfolgt Gespräche & Systemzustände über Speicherobjekte

📄 Lizenz & Autoren
Dieses Projekt steht unter der MIT License – siehe LICENSE.

Entwickelt im Rahmen des FUR CORE Projekts von Marcel S.

🤝 Contribution Guidelines
Forken & Branchen verwenden (feature/xyz)

Formatierung via make lint sicherstellen

Tests hinzufügen oder anpassen

Pull Request mit Beschreibung & Verweis auf Issues

🐞 Bekannte Probleme
🌐 Einige Übersetzungsdateien (translations/*.json) sind inkonsistent → i18n_tools/translate_sync.py verwenden

🔐 token.pickle muss lokal erzeugt sein für GCal OAuth

🧪 Einige Tests benötigen mongomock – ggf. separat installieren

📎 Ressourcen
Codex-Spezifikation.md – Funktionsübersicht & Designkonzept

AGENTS.md – Übersicht aller GPT-Agenten

CHANGELOG.md – Entwicklungshistorie

copilot-instructions.md – GPT/Copilot-Setup für Mitwirkende
