GitHub Copilot & ChatGPT (MARCEL) – Agentenanleitung
Dieses Repository nutzt GitHub Copilot (Codex) und ChatGPT (MARCEL) als unterstützende KI-Entwickler. Die Agenten helfen bei:

Feature-Entwicklung

Bugfixes

Refactoring

Testabdeckung

Code-Reviews

Dokumentation

Die Nachverfolgung von Aufgaben erfolgt über Jira und GitHub Issues. Diese Datei stellt sicher, dass beide Agenten effizient und regelkonform mit dem Projekt arbeiten.

🧑‍💻 Allgemeine Verhaltensregeln
Verstehe Aufgaben präzise. Konzentriere dich ausschließlich auf klar umrissene Anforderungen.

Begründe Änderungen. Verwende klare Commit-Botschaften und PR-Beschreibungen.

Erstelle Tests. Jede neue Funktion oder Bugfix muss durch Unit-Tests abgedeckt sein.

Kommentiere Code. Erkläre komplexe Logik, dokumentiere neue oder geänderte APIs.

Halte dich an Stilrichtlinien. Folge Projektkonventionen (z. B. PEP8, ESLint, gofmt).

🧹 Codeformatierung & Stil
Führe vor jedem Commit make fmt oder gleichwertige Formatierungsbefehle aus.

JavaScript/TypeScript: Doppelte Anführungszeichen, Tabs, ESLint.

Python: PEP8-konform (4 Leerzeichen, max. Zeilenlänge, sinnvolle Docstrings).

Verwende Projekt-Linter (npm run lint, make lint, etc.).

🔧 Build-, Test- & Lint-Prozesse
Build: make build, npm run build, docker build o. ä.

Test: make test, pytest, npm test je nach Stack.

Lint: Alle Linting-Fehler vorab beheben.

CI lokal: make ci führt alle Schritte in einem Durchlauf aus.

Docker: Optional über docker-compose mit zugehörigen Abhängigkeiten.

🔁 Pull Requests & Reviews
Keine Commits direkt auf main.

Jeder PR:

beschreibt was & warum (inkl. Jira-Issue-Link)

basiert auf einem Branch

nutzt bei Bedarf einen Draft

Code Review erfolgt iterativ:

Reviewer kommentieren gesammelt

Copilot verarbeitet Kommentare und pusht Verbesserungen

Merge nur bei:
✅ Build ✅ Lint ✅ Tests ✅ Review-Freigabe

📁 Projektstruktur
Ordner	Inhalt
src/	Hauptcode der Anwendung
lib/	Wiederverwendbare Module
tests/	Testfälle & Fixtures
docs/	Projektdokumentation
scripts/	Hilfsskripte
config/	Konfigurationen
.github/	Workflows, Templates, Agenten-Setup

🧠 Copilot/ChatGPT – Verhalten bei Aufgaben
Keine spekulativen Änderungen. Nur auf konkret beschriebene Issues reagieren.

Scoped arbeiten. Änderungsumfang auf das Nötigste begrenzen.

Struktur wahren. Verwende bestehende Module und Namenskonventionen.

Feedback einarbeiten. Nutze Reviewer-Kommentare zur Iteration.

Dokumentation synchron halten. Bei relevanten Änderungen auch docs/ aktualisieren.

🚀 Erweiterte Funktionen
⚙️ Setup-Datei copilot-setup-steps.yml
Installiert projektweite Abhängigkeiten vor Agentenlauf:

yaml
Kopieren
Bearbeiten
steps:
  - run: pip install -r requirements.txt
  - run: npm install
  - run: make build
🧩 Model Context Protocol (MCP)
Standardmäßig aktiv: GitHub MCP → Zugriff auf Issues, PRs, Commit-Metadaten

Lokale Tools: Optional via Actions-Container

Erweiterbar durch:

Playwright (Browser-Analyse)

Sentry (Fehlerkontext)

CI-Dashboards

Regel: Keine externen Server ohne Freigabe einbinden!

🔍 Fehlerbehandlung & Logs
Nutze Agenten-Logs zur Fehlerdiagnose (View logs in GitHub).

Typische Ursachen:

Fehlerhafte Branch-Basis

CI schlägt fehl (Format, Test, Build)

Unklare Aufgabenstellung

📚 Quellen & Referenzen
Best Practices: Copilot Coding Agent

Custom Instructions

Copilot Chat Cookbook

MCP & Erweiterungen

copilot-setup-steps.yml Guide
