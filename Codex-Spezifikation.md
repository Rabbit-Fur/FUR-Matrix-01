🛡️ FUR Command Center v2 – Offizielle Codex-Spezifikation.md
Stand: {{ heute }}
Status: 85 % produktiv, 15 % offen → bereit für finalen Ausbau

⚔️ Einleitung – Die Vision
Warriors of the FUR Alliance! Hear this decree!
From the deepest forges of code... arises our new center of power:
The FUR Command Center v2!

Dies ist mehr als nur ein Dashboard – es ist das strategische Herz unserer Allianz.
Ein Denkmal für Ehre, Organisation und Schlagkraft auf Server #28 und darüber hinaus.

🧩 Was es FÜR SPIELER bedeutet
✅ Event-Kalender
Alle Events auf einen Blick – via FullCalendar & Modals.

🔔 Reminder via Discord
Automatische Erinnerungen (1h / 10min vorher) via DM & Role Mention.

🔥 Teilnahme per Reaktion
Bot speichert alle :fire:-Reaktionen mit Event-ID in der DB.

🏆 Hall of Fame
Öffentliche Ruhmeshalle mit dynamischen Titeln & Champion-Postern.

📊 Leaderboards
Live-Rankings für:

Raids

Quests

Donations

📁 Ressourcen & Guides
Login-geschützt, Mehrsprachig, Downloadbereich.

🧠 Was es FÜR ADMINS bedeutet
🧰 Admin Dashboard
Sicher via Discord OAuth2 + R4/Admin Rollen

Event-CRUD in Sekunden

Teilnehmerlisten einsehbar

Datei-Upload mit Typ-/Größencheck

🖼️ Automatisierte Poster
Event-Poster bei Erstellung (Typ-abhängig)

Champion-Poster bei Monatsende

Webhook-Broadcast inklusive

🛡️ Security & Architektur
CSRF, SQL-Injection Proof

SECRET_KEY & Tokens via .env

Logging aktiv

Modular & skalierbar

🤖 DISCORD BOT FEATURES
Slash Commands
Befehl	Funktion
/add_event	Event erstellen
/events	Liste aller anstehenden Events
/leaderboard [x]	Rankings für Raids, Quests, Donations

Reminder
1h & 10m vor Event via DM

@Role Mention optional

Teilnahme
Reagiere mit 🔥 → Bot speichert Teilnehmer

🧭 WEB DASHBOARD FEATURES
Kalender (/calendar)
Visueller Kalender

Tooltip oder Modal bei Klick

Adminbereich (/admin)
Eventübersicht, Erstellung, Bearbeitung, Löschung

Teilnehmerübersicht

Datei-Upload

Übersetzungen zentral bearbeiten

Leaderboards (/leaderboards)
Tabs für Raids, Quests, Donations

Top-5 Listen mit Live-Werten aus DB

Wiederkehrende Events
Unterstützt weekly, monthly

Events werden automatisch generiert

🔐 INFRASTRUKTUR & SICHERHEIT
Discord OAuth2 mit ADMIN_ROLE_IDS

SESSION_SECRET & .env Management

Zugriffsschutz per Rollencheck

Session Timeout aktiv

Lokalisierung via Flask-Babel-NEXT

✅ STATUS: Vision vs. Realität
✅ Bereits vorhanden / umgesetzt
Bereich	Status	Details
Eventkalender	✅	FullCalendar aktiv + Modal/Details
Eventposter	✅	Dynamisch generiert, Discord Webhook
Reminder (Discord)	🔄 teilw.	Reminder aktiv, Opt-out fehlt noch
Emoji-Teilnahme	✅	:fire:-Tracking aktiv
Leaderboards	🔄 aktiv	Daten angezeigt, Caching fehlt
Champion-System	🔄 MVP	PIL Poster + Webhook aktiv, Auto-Berechnung ausstehend
Hall of Fame	✅	HTML-Seite lädt Champion-Daten
Slash Commands	✅	Funktionieren vollständig
Admin-Panel	✅	Login, Rollencheck, EventTools
Session-Handling	✅	Timeouts, CSRF, Schutz aktiv
Lokalisierung	✅	Deutsch/Englisch aktiv
Discord Poster	✅	Webhooks für Events & Champion

⚠️ Noch offen / vorbereitet
Feature	Status	Beschreibung
DM Opt-Out für Reminder/Newsletter	❌ fehlt	Teilnehmer können sich noch nicht abmelden
Leaderboard-Caching	🔄 fehlt	Rankings werden live berechnet, kein Cache vorhanden
Wöchentlicher Newsletter	❌ fehlt	newsletter_cog.py muss erstellt werden
Global ErrorHandler (Discord Bot)	❌ fehlt	Fehlerbehandlung nicht zentralisiert
Lokalisierte Slash-Befehle	❌ fehlt	Nur feste Strings
FLASK_ENV Schutzschalter	❌ fehlt	Reminder laufen auch in Dev-Umgebung
Google Calendar Sync	🟡 vorbereitet	Struktur vorhanden, Backend fehlt
WebSocket Live-Updates	🔲 möglich	Noch nicht eingebaut, architekturfähig
Rollenrechte im UI	🔄 grob	Backend prüft Rollen, aber kein UI-Rollenkonzept
Responsive Design	🔄 teilw.	Einige Seiten mobilfähig, andere nicht

📬 NEWSLETTER & DAILY MESSAGES
Wöchentlicher Newsletter (Sonntag 12:00 UTC)
text
Kopieren
Bearbeiten
FUR Alliance Weekly Overview

Welcome to another glorious week, warriors!
Here are your epic missions and events – don’t miss a thing!

───────  Upcoming Events ───────
[Event Title] – Tuesday, 30.04. 19:00 UTC
...

───────  Champion Zone ───────
Gather your participation, climb to the top, and become Champion of FUR!
Special rewards and eternal glory await our most active heroes!

───────  Important Notes ───────
Don’t forget to sign up for your events.
Check the calendar on the dashboard regularly.

Stay strong, stay FUR – Forge your Legend!
#FUR #Unity #Honor #Glory
Tägliche Erinnerung (jeden Tag 08:00 UTC)
text
Kopieren
Bearbeiten
FUR Alliance Daily Overview

Welcome to another glorious day, warriors!
Here are your epic missions and events – don’t miss a thing!

───────  Upcoming Events Today ───────
[Event Title] – Tuesday, 30.04. 19:00 UTC

───────  Champion Zone ───────
Gather your participation, climb to the top, and become Champion of FUR!
Special rewards and eternal glory await our most active heroes!

───────  Important Notes ───────
Don’t forget to sign up for your events.
Check the calendar on the dashboard regularly.

Stay strong, stay FUR – Forge your Legend!
#FUR #Unity #Honor #Glory
🛠 Technische To-Dos für Codex
Modul / Feature	Status	Aufgabe
newsletter_cog.py	❌ fehlt	Erstellung inkl. Loop + Formatierung
@tasks.loop(...)	🔄 nötig	Für täglichen & wöchentlichen Versand
get_events_for(date)	✅ bereit	DB-Query zur Event-Abfrage
format_events(events)	GPT-ready	GPT kann bei Textgenerierung helfen
Config.FLASK_ENV Schutz	❌ fehlt	Kein Versand im Dev-Modus
Opt-out Logik	❌ fehlt	Prüfen ob user reminder_optout == True
Logging + Rate-Limit Check	🔄 offen	DM-Versand statistisch tracken + Fehler erfassen
ErrorHandler (global)	❌ fehlt	Fehler zentral abfangen und Feedback an User liefern
