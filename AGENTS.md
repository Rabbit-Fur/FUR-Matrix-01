# 🧠 FUR SYSTEM – AGENTS.md  
**Codex Contributor Protocol** · Version: `QUM-1.0`  
**Repository**: [`Rabbit-Fur/try`](https://github.com/Rabbit-Fur/try)  
**Status**: 🔒 Production-grade · 🚧 Actively Maintained · 🤖 Codex Enhanced  

---

## 🔍 Projektstruktur – FUR MATRIX

| Ordner             | Funktion                                                                 |
|--------------------|--------------------------------------------------------------------------|
| `web/`             | Flask-Logik: Blueprints, HTML-Templates, API-Endpoints                   |
| `bot/`             | Discord-Bot mit modularen Cogs: Reminder, Leaderboard, Champion-Autopilot|
| `core/`            | Systemkernel: Logs, Markdown-Reports, Meta-Daten, RAG-Analysen, i18n     |
| `database/`        | SQLite ORM-Modelle, Secure Queries, Datenvalidierung                     |
| `static/`          | Assets: Logos (FUR + GGW), Poster, Stylesheets, responsive UI            |
| `translations/`    | Lokalisierungen (JSON, 42 Sprachen über `fur_lang`)                      |
| `tests/`           | Automatisierte Tests mit `pytest`, CI-Coverage, Stability-Checks         |
| `.github/workflows/`| CI/CD Pipelines, Codex-Integration, Auto-Releases                       |

---

## ⚙️ Lokales Setup

```bash
# 🔽 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 🧹 2. Linting & Formatierung prüfen
black . && isort . && flake8

# ✅ 3. Tests ausführen
pytest --disable-warnings --maxfail=1
```

---

## 🤖 Codex-Agent:innen: Arbeitsprotokoll

### 🪄 Codex-Task erstellen

```bash
codex-fur task "Fix reminder system import & add unit test"
```

### 📤 Task an Codex übergeben

```bash
codex-fur submit
```

### 🔁 Änderungen committen

```bash
pytest && git add . && git commit -m "✅ Fix: Reminder blueprint error + test"
```

---

## 🚀 Release-Flow (CI/CD + Auto-Deploy)

> Ausgelöst bei jedem PR auf `main` oder durch Codex Push.

### Schritte im Auto-Release:

1. 🔎 Lint & Syntaxprüfung  
2. 🧪 Tests & Coverage  
3. 📦 Build + Struktur-Check  
4. 🌐 Railway-Deployment  
5. 📣 Discord Webhook Push (Champion/Reminder)  
6. 📄 AGENTS.md & CHANGELOG.md Sync  

---

## 🧬 Codex-QUM Standards

| Kategorie           | Standardvorgabe                                                         |
|---------------------|--------------------------------------------------------------------------|
| Formatierung        | `black`, `isort`, `flake8`, keine Warnings im CI                        |
| Sprache             | Code: Englisch · UI: i18n via `fur_lang` (z. B. `de`, `en`, `tr`)       |
| Tests               | Pytest, Coverage min. 85 % bei neuen Features                           |
| Sicherheit          | Prepared Statements, Token-Protection, `.env` isoliert                  |
| Deployment          | Railway (Staging/Prod), mit ENV-Checks und Health Reports               |
| Branch-Naming       | `main` (Stable), `dev` (Integration), `codex/*` (Auto Tasks)            |
| Commits             | `🔁 Refactor`, `✅ Fix`, `➕ Feature`, `🧪 Test`, `🧹 Cleanup` etc.       |

---

## 🧭 Agent:innen-Verantwortung

Jede/r Contributor:in (egal ob Mensch oder Agent) verpflichtet sich zu:

- 🔒 Sicherem und dokumentiertem Arbeiten
- 🧠 Systemischen Denken (Matrix-Prinzip: Jede Änderung hat Kontext)
- 🧪 Test-getriebener Entwicklung
- 📄 Klare Protokollierung aller Änderungen

---

## 🛟 Kontakt & Support

| Ressource       | Zugang                                                                 |
|------------------|------------------------------------------------------------------------|
| 🤖 Codex         | [chatgpt.com/codex](https://chatgpt.com/codex)                         |
| 🐇 Owner         | `Rabbit#2142` auf Discord (Projektleitung)                             |
| ☁️ Deployment    | [Railway Dashboard](https://railway.app/project/fur-martix)            |
| 📦 GitHub Repo   | [`Rabbit-Fur/try`](https://github.com/Rabbit-Fur/try)                 |

---

## 📌 Letzter Validierter Zustand

- 🔖 Version: `v1.1.0.1`
- 🗓️ Release-Datum: 14.06.2025
- 🤖 Codex-Status: aktiviert (`codex-fur`)
- 🔄 Deployment: Live auf Railway (`fur-martix.up.railway.app`)
- 🛡️ Sicherheit: ENV/Token geschützt · Discord OAuth aktiv  

---

## 📣 Letzte Worte

> **Das FUR SYSTEM ist nicht nur ein Code-Repository.  
Es ist eine Allianz aus Effizienz, Automatisierung und Vertrauen.  
Jede Änderung zählt. Jeder Beitrag formt die Matrix.**
