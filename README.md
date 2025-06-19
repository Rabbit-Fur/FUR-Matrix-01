# FUR System

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

