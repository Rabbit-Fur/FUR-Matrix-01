# Fehlende oder nicht gesetzte Umgebungsvariablen / Secrets

| Variable | Verwendet in | Fehlt in | Beispielwert vorhanden |
|---------|--------------|---------|-----------------------|
| FUR_PAT | middleware/auth.js | .env.example, GitHub Secrets | Nein |
| PORT2 | app.js | .env.example, GitHub Secrets | Nein |
| DOCKER_REGISTRY | .github/workflows/deploy.yml | .env.example | Nein |
| DOCKER_IMAGE | .github/workflows/deploy.yml | .env.example | Nein |
| DOCKER_PASSWORD | .github/workflows/deploy.yml | .env.example | Nein |
| DOCKER_USERNAME | .github/workflows/deploy.yml | .env.example | Nein |
| DEPLOY_HOST | .github/workflows/deploy.yml | .env.example | Nein |
| DEPLOY_USER | .github/workflows/deploy.yml | .env.example | Nein |
| DEPLOY_KEY | .github/workflows/deploy.yml | .env.example | Nein |
| RAILWAY_TOKEN | .github/workflows/codex-fur-universal-railway.yml | .env.example | Nein |
