# 🧠 FUR SYSTEM – AGENTS.md
Codex Contributor Guide · Version: QUM-1.0  
Repository: `Rabbit-Fur/try`

---

## 📦 Matrix-Struktur (Projektübersicht)

| Verzeichnis     | Inhalt                                                                 |
|----------------|------------------------------------------------------------------------|
| `web/`         | Flask-Routen, HTML-Templates, API-Endpunkte (Blueprints)               |
| `bot/`         | Discord-Bot, Cogs, Reminder-System, Leaderboard                        |
| `core/`        | Logging, i18n, Meta-Daten, Markdown, Systemanalysen                    |
| `database/`    | SQLite-Modelle, DB-Zugriffe, Prepared Statements                        |
| `static/`      | Assets: Bilder, CSS, Champion-Poster, Branding                          |
| `tests/`       | Unit- & Integrationstests mit Pytest                                    |

---

## 🛠️ Setup-Anleitung für Codex-Agent:innen

Vor **jeder Änderung**:

```bash
# Vorbereitung
pip install -r requirements.txt

# Code-Formatierung & Schnelltests
black . && isort .
pytest --disable-warnings --maxfail=1
