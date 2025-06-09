"""Minimaler Einstiegspunkt zum lokalen Testen der Web-App."""

from web import create_app

# Lade die komplette Anwendung mit allen Blueprints
app = create_app()

if __name__ == "__main__":
    # Standard-Port und Debug-Modus für lokale Entwicklung
    app.run(port=8080, debug=True)
