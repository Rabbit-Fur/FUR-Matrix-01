# 🛰️ AGENTS.md – FUR SYSTEM (Codex QUM-1.0)

Dies ist die zentrale **Agentenübersicht und Codex-Registrierungsstelle** für alle aktiven Module im `agents/`-Verzeichnis von [`try`](https://github.com/Rabbit-Fur/try).  
Alle Agenten folgen dem Codex-Protokoll QUM-1.0 und implementieren klar abgegrenzte Verantwortlichkeiten.

---

## 📜 Codex-Anweisungen (QUM-1.0)

- Jeder Agent benötigt eine eigene `argend.md` im gleichen Ordner oder als eingebetteter Abschnitt im Modul.
- Agenten-Namen müssen dem Pattern `snake_case_agent.py` folgen (z. B. `reminder_agent.py`)
- Jeder Agent muss mindestens folgende Struktur enthalten:
  ```python
  class [Name]Agent(Agent):
      def __init__(self, *args):
          super().__init__(...)
          self.register_callback(...)
  ```
- Alle Agenten registrieren sich über `agenten_loader.py`
- Ein Agent darf **keine externen Requests** ohne deklarierte Abhängigkeit in `argend.md` durchführen.
- Zugriff auf `db`, `log`, `image_api`, `calendar_api`, `discord_bot` nur über Injectables / Codex-Komponenten
- Jeder Commit, der einen Agenten verändert, **muss** `COD:agent-name` als Prefix im Commit-Message enthalten.

> 🔒 Sicherheit: Alle `.env`-Abhängigkeiten **müssen** in `.env.example` dokumentiert sein.
> 📦 Deployment: Jeder Agent muss mit `make deploy-agent NAME=...` deploybar sein.
> 🧪 Jeder neue Agent benötigt mindestens 1 pytest-Funktion im Testordner `tests/`.

---

## 🗂️ Inhaltsverzeichnis

| Agent | Beschreibung |
|-------|--------------|
| [Inbox Agent](#📬-inbox-agent) | Verarbeitet Systemnachrichten intern/extern |
| [Access Agent](#🔐-access-agent) | Berechtigungen & Rollensystem |
| [Auth Agent](#🔑-auth-agent) | Authentifizierung via OAuth2 |
| [Champion Agent](#🏆-champion-agent) | Top-Spieler-Handling |
| [Dialog Agent](#💬-dialog-agent) | Multiturn-Dialogsteuerung |
| [Deployment Agent](#🚀-deployment-agent) | Auto-Deploy & Railway-Trigger |
| [Log Agent](#📑-log-agent) | Logging & AuditTrail |
| [Monitoring Agent](#📊-monitoring-agent) | Systemüberwachung |
| [Poster Agent](#🖼️-poster-agent) | Bildgenerierung & Posting |
| [PvP Meta Agent](#⚔️-pvp-meta-agent) | PvP-Meta-Rankings |
| [Reminder Agent](#⏰-reminder-agent) | Reminder-Logik |
| [Scheduler Agent](#📆-scheduler-agent) | Zeitplanung & Kalender-Logik |
| [Tagging Agent](#🏷️-tagging-agent) | Auto-Tagging |
| [Translation Agent](#🌐-translation-agent) | I18n-Unterstützung |
| [Webhook Agent](#🌍-webhook-agent) | Externe Event-Hooks |

---

## 📬 Inbox Agent
**Datei:** `agents/inbox_agent.py`  
Empfängt und verarbeitet eingehende Systemnachrichten (z. B. Discord, interne Trigger, E-Mails, Webhooks).  
→ Leitstelle für Message-Routing bei unbestimmten Eingangskanälen.

---

## 🔐 Access Agent
**Datei:** `agents/access_agent.py`  
→ Siehe `agents/access_argend.md`
Zentraler Agent für Rechteverwaltung: prüft Rollen, ACLs und Zugriff auf Channels, Kalender, Benutzer.  
→ Integriert mit MongoDB, Discord-Permissions, ggf. `firebase_claims`.

---

## 🔑 Auth Agent
**Datei:** `agents/auth_agent.py`  
→ Siehe `agents/auth_argend.md`
Authentifizierungsagent für alle OAuth2- und tokenbasierten Mechanismen.  
→ Verwaltet Login-Flows, Refresh-Tokens und Discord User-Identität.

---

## 🏆 Champion Agent
**Datei:** `agents/champion_agent.py`  
→ Siehe `agents/champion_argend.md`
Synchronisiert Spieler-Metadaten mit Leaderboards, XP-System, Titeln.  
→ Erlaubt Tracking von „Top Player“-Zuständen.

---

## 💬 Dialog Agent
**Datei:** `agents/dialog_agent.py`  
→ Siehe `agents/dialog_argend.md`
Ermöglicht stateful Dialoge über mehrere Turns hinweg.  
→ Bezieht sich auf Nutzerkontext, History, NLP oder Intent Matching.

---

## 🚀 Deployment Agent
**Datei:** `agents/deployment_agent.py`  
→ Siehe `agents/deployment_argend.md`
Managed Deployments über Railway, Trigger per Commit, Image Builds.  
→ Nutzt ggf. GitHub Webhooks oder CI/CD API.

---

## 📑 Log Agent
**Datei:** `agents/log_agent.py`  
→ Siehe `agents/log_argend.md`
Zentralisiertes Logging mit Zugriff auf `log.insert()` und Error-Persistenz in Mongo.  
→ Formatierter Output in STDOUT, Discord, UI.

---

## 📊 Monitoring Agent
**Datei:** `agents/monitoring_agent.py`  
→ Siehe `agents/monitoring_argend.md`
Agent für regelmäßige Health-Checks, Clusterstatus, OAuth-Gültigkeit.  
→ Optional mit Alert-Routing in `log_agent` oder Discord.

---

## 🖼️ Poster Agent
**Datei:** `agents/poster_agent.py`  
→ Siehe `agents/poster_argend.md`
Verwendet `image_api`, um dynamisch Poster, Kalender, Avatare zu rendern.  
→ Sendet Bild automatisch an Discord oder speichert in `cdn/`.

---

## ⚔️ PvP Meta Agent
**Datei:** `agents/pvp_meta_agent.py`  
→ Siehe `agents/pvp_meta_argend.md`
Verwaltet PvP-Metadaten, z. B. Team-Kombinationen, Klassen, Counter-Meta.  
→ Optional in Verbindung mit Champion-Agent.

---

## ⏰ Reminder Agent
**Datei:** `agents/reminder_agent.py`  
→ Siehe `agents/reminder_argend.md`
Speichert Reminder in `calendar_events`, sendet zur geplanten Zeit über Discord / Webhook.  
→ Unterstützt wiederkehrende Events, Wochentage, Zeitzonen.

---

## 📆 Scheduler Agent
**Datei:** `agents/scheduler_agent.py`  
→ Siehe `agents/scheduler_argend.md`
Verwaltet Planung, Kalendersynchronisation, Zeitblöcke.  
→ Kann automatisch Kalender aus Discord generieren.

---

## 🏷️ Tagging Agent
**Datei:** `agents/tagging_agent.py`  
→ Siehe `agents/tagging_argend.md`
Scannt Eingaben und weist automatisierte Tags / Kategorien zu.  
→ Unterstützt ML-Klassifikation oder Regex-Matching.

---

## 🌐 Translation Agent
**Datei:** `agents/translation_agent.py`  
→ Siehe `agents/translation_argend.md`
I18n-Handling (Internationalisierung), dynamische Übersetzungen basierend auf User-Sprache.  
→ Greift auf `i18n.json` oder externe Übersetzer zu.

---

## 🌍 Webhook Agent
**Datei:** `agents/webhook_agent.py`  
→ Siehe `agents/webhook_argend.md`
Verarbeitet externe POST-Ereignisse (GitHub, Stripe, andere Bots).  
→ Konvertiert in interne `AgentInput`-Events.

---

## 🧪 Tests
**Datei:** `agents/test_agents_init.py`  
Testet alle Agenten auf `register()`-Korrektheit und Ladefähigkeit durch `agenten_loader`.

---

## 📦 Agent Loader

**Datei:** `agents/agenten_loader.py`  
Zentrale Datei zur Registrierung aller Agenten bei Systemstart.  
→ Führt Import, Dependency Injection und `AgentRegistry`-Einträge aus.

---

## 🧬 Erweiterung

> Wenn ein neuer Agent hinzugefügt wird:
> - Datei unter `agents/`
> - Eintrag in `AGENTS.md`
> - `argend.md` anlegen
> - Tests definieren
> - `.env.example` prüfen/ergänzen

---

Stand: automatisch generiert durch Codex am 2025-07-02
