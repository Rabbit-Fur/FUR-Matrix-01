from datetime import datetime
import os

def generate_daily_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = f"core/logs/{today}-daily.md"
    os.makedirs("core/logs", exist_ok=True)

    content = f"""🕙 Daily Project & Learning Log – {today}

## Lernfortschritt Marcel
- Beispiel: Verständnis von `set`, `auto`, `getline()` in C++
- Sprachlogik: „no semantics“ = ohne Bedeutung

## Modulstatus
- ✅ FUR-LANG initialisiert
- ✅ Reminder-System aktiv
- 🟡 Champion-Modul teilweise aktiv
- 🔜 Kalender-Modul noch offen

## To-Do für morgen
- [ ] /hall-of-fame Seite fertigstellen
- [ ] Sprachauswahl integrieren
- [ ] Poster für Event visualisieren

## Bewertung
- Konsistenz: 9/10
- Modularität: 10/10
- Sicherheit: 8/10
- Design: 10/10
"""
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    generate_daily_log()
