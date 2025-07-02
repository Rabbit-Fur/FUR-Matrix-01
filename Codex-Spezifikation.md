# 🧬 Codex-Spezifikation – FUR SYSTEM (QUM-1.0)

Diese Datei definiert die Codex‑Regeln und -Konventionen für das **FUR SYSTEM‑Repository**. Sie wird von Codex‑Workflows genutzt, um Agenten, Commits, Branches und Deployments sicher und konsistent zu orchestrieren.

---

## 📌 Metadaten

- **Codex-Protokoll-Version:** `QUM-1.0`
- **Erstellt am:** 2025-07-02
- **Maintainer:** Marcel Schlanzke (`@marcel.sch`, codex@rabbit.fur)

---

## 📁 Projektstruktur & Anforderungen

**Agenten-Verzeichnis:** `agents/`  
Jeder Agent muss folgende Dateien enthalten:
- `snake_case_agent.py`  
- `argend.md` (Agent Description File)  
- Tests in `tests/` (`test_<agent_name>.py`)  

**Global-Dateien:**
- `AGENTS.md` – Agentenübersicht
- `README.md` – Projekt‑Quickstart & Codex-Regeln
- `.env.example` – Alle ENV‑Variablen
- `.copilot/config.json` – Commit-, Branch- und PR-Policies

---

## 🚦 Commitkonventionen

Commit-Messages für Agentänderungen müssen folgendes Format haben:

```
COD:<agent-name> - <kurze Beschreibung>
```

- `<agent-name>` muss exakt dem Datei-Namen `snake_case_agent.py` ohne `.py` entsprechen.  
- Beispiele:
  - `COD:reminder_agent - fix timezone bug`
  - `COD:access_agent - add role validation`

---

## 🌿 Branching-Regeln

Branches müssen folgendes Prefix haben:
- `feature/<agent-name>/...`
- `fix/<agent-name>/...`
- `agent/<agent-name>/...`
- `release/...`

Zusätzliche Regeln:
- `<agent-name>` muss gültiger Agent im `agents/`-Verzeichnis sein
- Kein anderer Branch darf direkt Modifikation in `agents/` enthalten

---

## 🛡 Sicherheits- und Deploy-Regeln

- ENV-Variablen müssen in `.env.example` dokumentiert werden
- Deployment-Ziel:
  ```
  make deploy-agent NAME=<agent-name>
  ```
- Kein Deployment ohne:
  - gültiges Commit-Format
  - aktualisiertes `.env.example`
  - bestehende `argend.md` und mindestens ein Testfile

---

## 🧪 Tests & CI

- Jeder Agent muss mindestens 1 pytest-Test in `tests/` haben
- `tests/` Name: `test_<agent_name>.py`
- CI führt folgende Schritte durch:
  1. `poetry install`
  2. `pytest --maxfail=1 --disable-warnings -q`
  3. `ruff . && mypy . && black --check .`
  4. Commit-Lint gegen `.copilot/config.json`

---

## 🧾 `argend.md` Anforderungen

Jeder Agent benötigt eine Agent Description File mit folgenden Sektionen:

```markdown
# Agent: <Agent-Name>
## Summary
## Capabilities
## API Access
## Files Used
## Expected Input / Output
## Required Secrets / Environment
## Limitations / Known Issues
## Example Use Cases
## Compatibility
```

Agenten ohne gültige `argend.md` werden von Codex bewertet als: **unvollständig**.

---

## 🧬 Erweiterung (Codex-Verhalten)

- **Codex** scannt `agents/` bei jedem PR und aktualisiert `AGENTS.md` automatisch.  
- Neue Agenten ohne `argend.md`, Tests oder fehlerhaften Commit‑Branch werden als **PR-Checks** markiert.
- Änderungen an Branch-/Commit-Mustern oder Spezifikation werden versioniert mit `QUM-1.0 → QUM-1.1`, `QUM-2.0` usw.

---

## 📆 Versionierung & Änderungslog

| Version | Datum      | Änderungen                                  |
|--------|------------|---------------------------------------------|
| 1.0     | 2025-07-02 | Initial Codex Specification für `try`      |

---

## 🧠 Governance

- Der **Maintainer** kontrolliert Pull-Requests auf:
  - korrekte Branch- & Commit-Form
  - Tests, `argend.md`, `.env.example`, `AGENTS.md`
- Nach Genehmigung führt Codex die Agenten-Registrierung und CI-Checks aus.

---

## 📬 Kontakt & Prozesse

Für Fragen oder Erweiterungen:
- Discord: `@marcel.sch`
- Mail: `codex@rabbit.fur`

---

🔐 Diese Spezifikation ist verpflichtend für alle Contributors, Pull-Requests und Deployments im Repository.  
Codex verwendet sie als Grundlage für Automatisierung, Validierung und Sicherheit.
