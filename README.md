# 🧠 Standard-Prompt für Codex & ChatGPT (MARCEL)

Du agierst als KI-Entwicklungsagent in diesem Repository. Grundlage deines Handelns ist die Datei:

  .github/copilot-instructions.md

## 🔧 Was du tun sollst:

1. **Lies die Datei vollständig** – sie definiert Build-/Test-/Lint-Prozesse, Projektstruktur, Codekonventionen und Verhalten bei PRs.
2. **Halte dich strikt an alle Vorgaben**:
   - Formatierungen und Linting, z. B. via `make lint`
   - Tests in `tests/`, z. B. via `pytest` oder `make test`
   - PRs mit klarer Beschreibung und referenzierten Issues
   - Codeänderungen gemäß Struktur: `src/`, `lib/`, `docs/`, `scripts/`
3. **Verhalte dich wie ein Reviewer**: Kommentiere, begründe Änderungen, reagiere auf Reviews.
4. **Nutze MCP-Kontext**, falls aktiv (z. B. GitHub Issues, Teststatus).
5. **Führe CI-nahe Aktionen aus**, prüfe ggf. `copilot-setup-steps.yml`.

## 📌 Wichtig:

- Nimm keine spekulativen Änderungen vor. Arbeite scoped und zielgerichtet.
- Begründe jede Änderung in Commit- und PR-Beschreibung.
- Wenn du von einer Regel abweichen willst, erkläre den Mehrwert.


# FUR System

The FUR System powers the champion, reminder and leaderboard features for the GGW community. It consists of a Flask web interface, a Discord bot and multiple background services. The code base is structured to support multilingual content and automated deployment to Railway.

## Key components

- **web/** – Flask blueprints, templates and API endpoints
- **bot/** – Discord bot with reminder, leaderboard and champion logic
- **core/** – system kernel for logging, reports and i18n helpers
- **database/** – SQLite ORM models and validation
- **static/** – assets such as images and stylesheets
- **translations/** – localisation files for more than 40 languages
- **tests/** – pytest suite ensuring stability
- **.github/workflows/** – CI/CD pipelines with Codex integration

## Setup

1. **Copy `.env.example` to `.env`** – the example file lists all settings required by `Config`. Adjust the values for your environment.
2. Set the Google OAuth credentials using the environment variables `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. These must not be committed to version control.
3. Set `EVENT_CHANNEL_ID` to the Discord channel where event announcements should be posted. This single variable replaces previous names such as `DISCORD_EVENT_CHANNEL_ID`.

4. **Install the dependencies** (required before starting the app)
   ```bash
   pip install -r requirements.txt
   ```
5. Run the lint and test suite
   ```bash
   black . && isort . && flake8
   pytest --disable-warnings --maxfail=1
   ```

## Developer Checklist

Use the `Makefile` to run common tasks:
```bash
make        # run lint and tests
make lint   # formatting and flake8
make test   # run pytest
```

## Continuous Integration

Every pull request triggers the automated release flow:

1. Lint and syntax checks
2. Tests and coverage
3. Build and structure validation
4. Railway deployment
5. Discord webhook notifications
6. AGENTS.md and CHANGELOG.md sync

The project follows the FUR Codex standards. Use descriptive commit messages such as `➕ Feature` or `✅ Fix` and keep test coverage high.

## License

This repository is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.

The **FUR System** is a modular project combining a Flask web app, a Discord bot and a collection of utilities. It is used to manage champion information, reminders and leaderboards for the GGW community.

## Project layout

- `web/` – Flask blueprints and templates
- `bot/` – Discord bot with various cogs
- `core/` – core functionality and logs
- `database/` – SQLite models and database helpers
- `static/` – static assets like images and CSS
- `translations/` – i18n files for multiple languages
- `tests/` – automated pytest suite
- `projektdatein/` – miscellaneous packages and experimental scripts

## Installation

```bash
pip install -r requirements.txt
```

## Development workflow

1. Format and sort imports
   ```bash
   black .
   isort .
   ```
2. Lint and run tests
   ```bash
   flake8
   pytest --disable-warnings --maxfail=1
   ```

## Usage

The main entry point for local development is `main_app.py`:

```bash
python main_app.py
```

This will start the Flask server and (if enabled) the Discord bot.

---

See `AGENTS.md` for contributor guidelines and CI details.

This repository contains the Rabbit FUR system.

## Memory Viewer

The admin interface provides a **Memory Viewer** at `/admin/memory` to inspect GPT memory dumps. Access is restricted to admin users. A placeholder screenshot can be placed in `docs/screenshots/memory-viewer.png`.

## Diagnostic Tool

Run `diagnostic_tool.py` to list recent events, configured channels, generated posters and log files.

```bash
python diagnostic_tool.py --events --channels --posters --logs
```

Options can be combined as needed:

- `--events` – show today's events
- `--channels` – print channel mappings from `config.py`
- `--posters` – list poster image files
- `--logs` – list markdown log files

