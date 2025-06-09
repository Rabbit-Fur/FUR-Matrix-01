# Codex Agent Guide – FUR SYSTEM

## 🗂 Projektstruktur
- Flask Web-Backend: `main/`
- Discord Bot: `bot/`
- Mehrsprachigkeit: `main/translations/`

## 🛠 Tools & Linting
- Formatter: `black .` + `isort .`
- Testbefehl: `python3 -m unittest discover`
- Starten: `python3 main/app.py`

## 🧾 Fokusaufgaben für Codex
- Vervollständigung aller Übersetzungen in `main/translations/`
- Validierung von JSON-Strukturen & Einheitlichkeit der Keys
- Reminder-Modul prüfen (Zeitsteuerung, DMs, Sprachintegration)
- Zugriffsprüfung für R3/R4/ADMIN bei allen Routen

## 🧪 Codex soll...
- PRs nur über `main` erzeugen
- Python 3.11 verwenden
- Änderungen über Pull Requests einreichen
