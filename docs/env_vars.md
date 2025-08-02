# Environment Variables

The following table lists all variables accessed in the codebase. Locations refer to the main modules where they are read.

| Variable | Location (examples) | Purpose |
|----------|--------------------|---------|
| ADMIN_ROLE_IDS | config.py, agents/access_agent.py | Discord role IDs with admin privileges |
| BABEL_DEFAULT_LOCALE | fur_lang/i18n.py | Default locale for Flask-Babel |
| BASE_URL | config.py, core/universal/setup.py | Public application base URL |
| CODEX_ENV_GO_VERSION | core/universal/setup.py | Version hint for Go runtime |
| CODEX_ENV_NODE_VERSION | core/universal/setup.py | Version hint for Node runtime |
| CODEX_ENV_PYTHON_VERSION | core/universal/setup.py | Version hint for Python runtime |
| CODEX_ENV_RUST_VERSION | core/universal/setup.py | Version hint for Rust runtime |
| CODEX_ENV_SWIFT_VERSION | core/universal/setup.py | Version hint for Swift runtime |
| DATABASE_URL | — | Optional alternative database connection string |
| DEBUG | main_app.py | Enable debug mode |
| DISCORD_CLIENT_ID | config.py | Discord OAuth client ID |
| DISCORD_CLIENT_SECRET | config.py | Discord OAuth client secret |
| DISCORD_GUILD_ID | config.py | Discord guild/server ID |
| DISCORD_REDIRECT_URI | config.py | Redirect URI for Discord OAuth |
| DISCORD_TOKEN | config.py, core/universal/setup.py | Bot token for Discord |
| DISCORD_WEBHOOK_URL | config.py, dashboard/weekly_log_generator.py | Webhook for Discord messages |
| ENABLE_CHANNEL_REMINDERS | bot/cogs/reminders.py | Toggle reminder messages in channels |
| ENABLE_DISCORD_BOT | main_app.py, bot/bot_main.py | Start real Discord bot |
| ENABLE_NEWSLETTER_AUTOPILOT | bot/cogs/newsletter_autopilot.py | Enable newsletter cron |
| ENV_FILE | config.py | Path to `.env` file |
| EVENT_CHANNEL_ID | config.py | Optional event channel ID |
| FLASK_ENV | config.py, fur_lang/i18n.py | Flask environment (`production` or `development`) |
| FLASK_SECRET | main_app.py, web/__init__.py | Flask secret key if not set via `SECRET_KEY` |
| GITHUB_TOKEN | README.md | Token for GitHub actions |
| GOOGLE_AUTH_PROVIDER_CERT_URL | .env.example | Certificate URL for Google OAuth validation |
| GOOGLE_AUTH_URI | .env.example | OAuth auth endpoint |
| GOOGLE_CALENDAR_ID | config.py, google_calendar_sync.py | Google Calendar ID used for sync |
| GOOGLE_CALENDAR_SCOPES | .env.example | Scopes for calendar write access |
| GOOGLE_CLIENT_CONFIG | google_oauth_setup.py, web/routes/google_oauth_web.py | Path to Google client config JSON |
| GOOGLE_CLIENT_CONFIG_FILE | google_auth.py | Path to Google OAuth client config JSON |
| GOOGLE_CLIENT_ID | config.py | Google OAuth client ID |
| GOOGLE_CLIENT_SECRET | config.py | Google OAuth client secret |
| GOOGLE_CREDENTIALS_FILE | config.py, google_calendar_sync.py, google_auth.py | OAuth token storage path |
| GOOGLE_CREDENTIALS_FILE | config.py, google_calendar_sync.py | Service account credentials file |
| GOOGLE_PROJECT_ID | .env.example | Google Cloud project ID |
| GOOGLE_REDIRECT_URI | config.py, web/routes/google_oauth_web.py | OAuth redirect URI |
| GOOGLE_SCOPES | .env.example | Scopes for read-only calendar access |
| GOOGLE_SYNC_INTERVAL_MINUTES | config.py, utils/google_sync_task.py | Interval for calendar sync |
| GOOGLE_TOKEN_STORAGE_PATH | .env.example | Path to stored OAuth tokens |
| GOOGLE_TOKEN_URI | .env.example | OAuth token endpoint |
| HoF_CHANNEL_ID | .env.example | Channel for Hall of Fame posts |
| LEADERBOARD_CHANNEL_ID | .env.example | Channel for leaderboard updates |
| LOGTAIL_TOKEN | .env.example | Token for Logtail logging |
| MONGO_DB | config.py, mongo_service.py | MongoDB database name |
| MONGO_PASSWORD | .env.example | Password for MongoDB authentication |
| MONGO_URL | init_daily_logs.py | Simple Mongo connection URL for scripts |
| MONGODB_URI | config.py, mongo_service.py | MongoDB connection URI |
| NEWSLETTER_DM_DELAY | bot/cogs/newsletter_autopilot.py | Delay between DM sends |
| OPENAI_API_KEY | i18n_tools/translate_sync.py | OpenAI API authentication |
| PORT | main_app.py | HTTP server port |
| PORT2 | .env.example | Secondary port for auxiliary services |
| PROMETHEUS_ENDPOINT | README.md | Prometheus metrics endpoint (default http://localhost:9090) |
| public_CHANNEL_ID | .env.example | Channel for public announcements |
| RAILWAY_PROJECT | .env.example | Railway project identifier |
| RAILWAY_TOKEN | .env.example | Railway API token for deployment |
| R3_ROLE_IDS | config.py | Discord role IDs for R3 group |
| R4_ROLE_IDS | config.py | Discord role IDs for R4 group |
| REMINDER_CHANNEL_ID | config.py, bot/cogs/reminders.py | Channel for reminder posts |
| REMINDER_DM_DELAY | bot/cogs/reminder_autopilot.py | Delay for DM reminders |
| REMINDER_ROLE_ID | config.py | Discord role for reminder pings |
| REPO_GITHUB | utils/github_service.py, services/github_sync.py | Default GitHub repository |
| SECRET_KEY | config.py | Flask session secret |
| SESSION_LIFETIME_MINUTES | config.py | Lifetime for user sessions |
| TOKEN_GITHUB_API | utils/github_service.py | GitHub API token |
| TOKEN_GITHUB_SYNC | services/github_sync.py | Token for sync service |
| DEFAULT_DM_IMAGE_URL | config.py | Default image for Discord DMs |
| POSTER_OUTPUT_PATH | config.py | Directory for generated posters |
| FUR_PAT | middleware/auth.js | Personal access token for Node middleware |

