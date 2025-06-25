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

Copy `.env.example` to `.env` and adjust the values for your environment before running the setup commands.

Set `EVENT_CHANNEL_ID` to the Discord channel where event announcements should be posted.

1. **Install the dependencies** (required before starting the app)
   ```bash
   pip install -r requirements.txt
   ```
2. Run the lint and test suite
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

