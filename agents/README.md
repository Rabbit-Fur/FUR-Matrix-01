# 🤖 FUR Agenten-System

Dieses Modul enthält alle spezialisierten Agenten für das FUR SYSTEM – modular, erweiterbar und sofort einsatzfähig.

## 📁 Enthaltene Agenten (Stand: 16.06.2025)

| Agent             | Datei                    | Beschreibung |
|------------------|--------------------------|--------------|
| `AccessAgent`     | `access_agent.py`         | Verifiziert Rollen (R3/R4/Admin), Discord-Zugang, Berechtigungen |
| `AuthAgent`       | `auth_agent.py`           | Authentifiziert Discord-User, prüft Sessions |
| `ChampionAgent`   | `champion_agent.py`       | Erzeugt Champion-Poster, Discord-Webhook, HoF-Eintrag |
| `DeploymentAgent` | `deployment_agent.py`     | Erstellt ZIPs, Releases, prüft Tokens, triggert CI/CD |
| `DialogAgent`     | `dialog_agent.py`         | Antwortet kontextuell auf User-Fragen (z. B. „hilfe“) |
| `InboxAgent`      | `inbox_agent.py`          | Speichert Discord-DMs wie `/join_event`, `/feedback` |
| `LogAgent`        | `log_agent.py`            | Generiert Markdown-Daily/Wochen-Logs |
| `MigrationAgent`  | `migration_agent.py`      | Führt SQLite → MongoDB Migrationen durch |
| `MonitoringAgent` | `monitoring_agent.py`     | Führt Healthchecks, Statusprüfungen und Logging aus |
| `PvPMetaAgent`    | `pvp_meta_agent.py`       | Analysiert Enforcer/Skills, erstellt Tierlists |
| `ReminderAgent`   | `reminder_agent.py`       | Versendet Discord-Reminder, Opt-Out Verwaltung |
| `SchedulerAgent`  | `scheduler_agent.py`      | Zeitgesteuerte Aufgaben (Loops, Reminder, CRON) |
| `TaggingAgent`    | `tagging_agent.py`        | Erstellt automatisch Hashtags, PvP-Kategorien |
| `TranslationAgent`| `translation_agent.py`    | Synchronisiert `.json`-Sprachdateien, GPT-Übersetzung |
| `WebhookAgent`    | `webhook_agent.py`        | Versendet Discord-/CI-/Log-Webhook-Nachrichten |

---

## 🔧 Initialisierung

Verwende folgenden zentralen Loader:

```python
from agents.agenten_loader_ext import init_all_agents

agents = init_all_agents(db, session)
agents["reminder"].send_reminders()
