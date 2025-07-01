🧠 FUR SYSTEM – AGENTS.md
Codex Contributor Protocol · Version: QUM-1.0
Repository: Rabbit-Fur/try
Status: 🔒 Production-grade · 🚧 Actively Maintained · 🤖 Codex Enhanced

---

🔍 Projektstruktur – FUR MATRIX

| Ordner               | Funktion                                                         |
| -------------------- | ---------------------------------------------------------------- |
| `web/`               | Flask-Logik: Blueprints, HTML-Templates, API-Endpoints           |
| `bot/`               | Discord-Bot mit modularen Cogs: Reminder, Leaderboard, Autopilot |
| `core/`              | Systemkernel: Logs, Markdown-Reports, Meta-Daten, RAG, i18n      |
| `database/`          | SQLite ORM-Modelle, Secure Queries, Datenvalidierung             |
| `static/`            | Assets: Logos (FUR + GGW), Poster, Stylesheets, responsive UI    |
| `translations/`      | Lokalisierungen (JSON, 42 Sprachen via `fur_lang`)               |
| `tests/`             | Automatisierte Tests mit pytest, CI-Coverage, Stability-Checks   |
| `.github/workflows/` | CI/CD Pipelines, Codex-Integration, Auto-Releases                |

---

⚙️ Lokales Setup

```bash
# 🔽 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 🧹 2. Linting & Formatierung prüfen
black . && isort . && flake8

# ✅ 3. Tests ausführen
pytest --disable-warnings --maxfail=1
```

---

🤖 Codex-Agent\:innen: Arbeitsprotokoll

🪄 Codex-Task erstellen

```
codex-fur task "Fix reminder system import & add unit test"
```

📤 Task an Codex übergeben

```
codex-fur submit
```

🔁 Änderungen committen

```
pytest && git add . && git commit -m "✅ Fix: Reminder blueprint error + test"
```

🚀 Release-Flow (CI/CD + Auto-Deploy)

* Ausgelöst bei jedem PR auf `main` oder durch Codex Push.

**Ablauf:**

* 🔎 Lint & Syntaxprüfung
* 🧪 Tests & Coverage
* 📦 Build + Struktur-Check
* 🌐 Railway-Deployment
* 📣 Discord Webhook Push (Champion/Reminder)
* 📄 AGENTS.md & CHANGELOG.md Sync

---

🧬 Codex-QUM Standards

| Kategorie     | Standardvorgabe                                         |
| ------------- | ------------------------------------------------------- |
| Formatierung  | `black`, `isort`, `flake8`, keine Warnings im CI        |
| Sprache       | Code: Englisch · UI: i18n via `fur_lang`                |
| Tests         | `pytest`, Coverage min. 85 % bei neuen Features         |
| Sicherheit    | `.env`-basierte Tokens, keine Secrets im Code           |
| Deployment    | Railway (Staging/Prod), ENV-Checks, Health Reports      |
| Branch-Naming | `main`, `dev`, `codex/*`                                |
| Commits       | 🔁 Refactor, ✅ Fix, ➕ Feature, 🧪 Test, 🧹 Cleanup etc. |

---

📐 Codex-Ausführungsrichtlinien (verbindlich für alle Tasks)

🧠 Du bist ein erfahrener Backend-Ingenieur für das MARCEL / FUR CORE System. Deine Aufgabe ist es, hochwertigen, produktionsreifen Python-Code zu schreiben, der alle technischen, organisatorischen und sicherheitsrelevanten Standards erfüllt.

### Berücksichtige bei jeder Aufgabe zwingend folgende Richtlinien:

✅ **CODE-QUALITÄT & PRÜFUNG**

* Code muss mit `pytest` getestet sein
* Linting: `black --check .`, `flake8` fehlerfrei
* Gilt immer, außer bei reiner Doku/Kommentar-Änderung

🔐 **SICHERHEIT & TOKEN-HANDLING**

* Keine Tokens/Secrets im Quellcode
* Nur Zugriff über `.env`, `os.getenv`
* Gültige Zugriffstokens bei API-Nutzung (z. B. Google)

🌐 **NETZWERK & SYSTEM-ZUGRIFF**

* Internetzugriff vollständig erlaubt
* Zugriff auf alle Domains erlaubt
* HTTP-Methoden: `GET`, `POST`, `PUT`, `PATCH`, `DELETE` – alle erlaubt und zu verwenden

📆 **KALENDER-FUNKTIONALITÄT**

* Mongo-kompatibles Event-Format: `google_id`, `start`, `event_time`, `summary`, …
* Collection: `calendar_events` in DB `furdb`
* Keine Duplikate: `google_id` checken oder Upsert

🌀 **DISCORD-SYSTEM**

* Cogs müssen Events korrekt empfangen
* Keine Endlosschleifen durch Selbstupdates

🌱 **KONFIGURATION & UMGEBUNG**

* Keine harten Pfade – nutze `.env`, `os.getenv`

📂 **STRUKTURKONTEXT**

* Integration in bestehende Dateien wie `try-main.zip`, `google_calendar.py`, `event_model.py`, `logger.py`
* Modularität, Wiederverwendbarkeit, Logging und Exception-Handling beachten

📌 **OUTPUT-VORGABE**

* Nur lauffähiger Code
* Keine Kommentare oder Meta-Beschreibung
* Nur notwendige Imports
* Logging via `utils/logger.py`, falls vorhanden

---

🛟 Kontakt & Support

| Ressource      | Zugang                                                                 |
| -------------- | ---------------------------------------------------------------------- |
| 🤖 Codex       | [https://chatgpt.com/codex](https://chatgpt.com/codex)                 |
| 🐇 Owner       | Rabbit#2142 auf Discord                                                |
| ☁️ Deployment  | Railway Dashboard                                                      |
| 📦 GitHub Repo | [https://github.com/Rabbit-Fur/try](https://github.com/Rabbit-Fur/try) |

---

📌 Letzter Validierter Zustand

* 🔖 Version: v1.1.0.2
* 🗓️ Release-Datum: 14.06.2025
* 🤖 Codex-Status: aktiviert (`codex-fur`)
* 🔄 Deployment: Live auf Railway (fur-martix.up.railway.app)
* 🛡️ Sicherheit: ENV/Token geschützt · Discord OAuth aktiv

📣 **Letzte Worte**

> Das FUR SYSTEM ist nicht nur ein Code-Repository. Es ist eine Allianz aus Effizienz, Automatisierung und Vertrauen.
> Jede Änderung zählt. Jeder Beitrag formt die Matrix.
