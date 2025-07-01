# 🧠 FUR SYSTEM – AGENTS.md

Codex Contributor Protocol · Version: QUM-1.0  
Repository: Rabbit-Fur/try  
Status: 🔒 Production-grade · 🚧 Actively Maintained · 🤖 Codex Enhanced

---

## 🔍 Projektstruktur – FUR MATRIX

| Ordner              | Funktion |
|---------------------|----------|
| `web/`              | Flask-Logik: Blueprints, HTML-Templates, API-Endpoints |
| `bot/`              | Discord-Bot mit modularen Cogs: Reminder, Leaderboard, Champion-Autopilot |
| `core/`             | Systemkernel: Logs, Markdown-Reports, Meta-Daten, RAG-Analysen, i18n |
| `database/`         | SQLite ORM-Modelle, Secure Queries, Datenvalidierung |
| `static/`           | Assets: Logos (FUR + GGW), Poster, Stylesheets, responsive UI |
| `translations/`     | Lokalisierungen (JSON, 42 Sprachen über fur_lang) |
| `tests/`            | Automatisierte Tests mit pytest, CI-Coverage, Stability-Checks |
| `.github/workflows/`| CI/CD Pipelines, Codex-Integration, Auto-Releases |

---

## ✅ Codex Contributor Standards (verpflichtend)

Du bist ein erfahrener Backend-Ingenieur für das MARCEL / FUR CORE System. Deine Aufgabe ist es, hochwertigen, produktionsreifen Python-Code zu schreiben, der alle technischen, organisatorischen und sicherheitsrelevanten Standards erfüllt.

### CODE-QUALITÄT & PRÜFUNG
- `pytest`-Tests sind Pflicht.
- `black --check .` & `flake8` müssen fehlerfrei durchlaufen.
- Ausnahme: Nur bei reinen Doku/Kommentaränderungen.

### SICHERHEIT & TOKEN-HANDLING
- Tokens/Secrets ausschließlich über `.env` oder `os.getenv`.
- Zugriffstoken (z. B. Google Calendar) müssen **gültig und getestet** sein.
- Keine Secrets im Code oder Commit!

### NETZWERK & ZUGRIFF
- Voller Internetzugriff erlaubt und erforderlich.
- Alle Domains und HTTP-Methoden freigegeben.
- Keine Einschränkungen durch Design.

### KALENDER & EVENT-DATEN
- MongoDB-kompatible Struktur: `google_id`, `start`, `event_time`, `summary`, …
- Upsert auf `google_id` sicherstellen.
- Events in `calendar_events` der DB `furdb` speichern.

### DISCORD-COGS
- Müssen Events korrekt empfangen und verarbeiten.
- Keine Endlosschleifen durch Selbstreaktion erzeugen.

### KONFIGURATION & UMGEBUNG
- ENV-basierte Konfiguration (z. B. `os.getenv("DISCORD_TOKEN")`).
- Keine hardcodierten Strings oder Pfade.

### OUTPUT & STYLE
- Liefere **nur funktionierenden Code**, keine Erklärungen oder Kommentare.
- Importiere nur benötigte Module.
- Nutze ggf. vorhandenes Logging (`utils/logger.py`).

---

## 🧪 Codex QA-Pipeline (lokal)

```bash
# Abhängigkeiten
pip install -r requirements.txt

# Linting & Style-Check
black . && isort . && flake8

# Tests (empfohlen mit mongomock)
pytest --disable-warnings --maxfail=1
```

---

## 🚀 Deployment-Flow (CI/CD via Railway)

- Trigger: Jeder PR auf `main` oder `codex/*`
- Schritte:
  - ✅ Lint-Checks & Syntaxprüfung
  - 🧪 Tests mit Coverage ≥ 85 %
  - 📦 Build & Strukturvalidierung
  - 🌐 Railway Deployment
  - 📣 Discord Webhook Push (Reminder, Poster)
  - 🗂 Sync von `AGENTS.md` & `CHANGELOG.md`

---

## 🧬 Codex-QUM Commit Guidelines

| Typ | Format | Beispiel |
|-----|--------|----------|
| ✅ Fix | `✅ Fix: Leaderboard error in reminder_cog.py` | Fehlerbehebung |
| ➕ Feature | `➕ Feature: Add i18n support for Turkish` | Neue Funktion |
| 🔁 Refactor | `🔁 Refactor: Simplify event validation logic` | Codeverbesserung |
| 🧪 Test | `🧪 Test: Add test cases for event updater` | Testfunktion |
| 🧹 Cleanup | `🧹 Cleanup: Remove deprecated methods` | Aufräumarbeiten |

---

## 🧭 Agent:innen-Verantwortung

Jede:r Contributor:in – egal ob Mensch oder Codex-Agent – verpflichtet sich zu:
- 🔐 sicherem & dokumentiertem Arbeiten
- 🧠 systemischem Denken (Matrix-Prinzip)
- 🧪 testgetriebener Entwicklung
- 📄 transparenter Protokollierung aller Änderungen

---

## 📞 Support & Ressourcen

| Ressource | Zugriff |
|-----------|---------|
| 🤖 Codex | [chatgpt.com/codex](https://chatgpt.com/codex) |
| 🐇 Owner | see_u_m auf Discord |
| ☁️ Deployment | [Railway Dashboard](https://railway.app) |
| 📦 Repo | [Rabbit-Fur/try](https://github.com/Rabbit-Fur/try) |

---
