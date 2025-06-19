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

```bash
pip install -r requirements.txt
black . && isort . && flake8
pytest --disable-warnings --maxfail=1
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
