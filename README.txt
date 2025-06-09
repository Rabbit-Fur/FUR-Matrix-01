# FUR System

Dieses Projekt enthält das Web-Portal und den Discord-Bot. Für einen lokalen Start sind einige Umgebungsvariablen erforderlich.

## Lokale Ausführung

1. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

2. Benötigte Umgebungsvariablen setzen (Beispiel):

```bash
export SECRET_KEY=dev
export DISCORD_TOKEN=<your token>
export DISCORD_GUILD_ID=1
export DISCORD_CHANNEL_ID=1
export DISCORD_CLIENT_ID=<client id>
export DISCORD_CLIENT_SECRET=<client secret>
export DISCORD_REDIRECT_URI=http://localhost:8080/login/discord/callback
```

3. Anwendung starten:

```bash
python main_app.py
```

Das Skript `mini.py` ist lediglich für kurze Tests gedacht und lädt keine Blueprints. Für die vollständige Anwendung mit Discord-Login muss `main_app.py` (oder `gunicorn main_app:app`) verwendet werden.
