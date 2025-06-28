GitHub Copilot und ChatGPT Anweisungen

Dieses Repository nutzt GitHub Copilot (Codex) und ChatGPT (intern „MARCEL“ genannt) als unterstützende KI-Entwickler. Sie helfen beim Implementieren von Features, Reviewen von Code, Schreiben und Ausführen von Tests, Refactoring sowie Bugfixing. Die Nachverfolgung von Aufgaben erfolgt über Jira. Diese Anleitung stellt sicher, dass die KI-Agenten effektiv im Einklang mit unseren Entwicklungsstandards arbeiten. Bitte befolgen Sie die folgenden Richtlinien, damit Copilot und ChatGPT unsere Arbeitsabläufe optimal unterstützen.


Code-Formatierung und Stil


Format-Tool nutzen: Führe vor jedem Commit das Formatierungstool aus (z. B. make fmt), um konsistente Code-Formatierung sicherzustellen. Dies stellt sicher, dass der Code einheitlich formatiert ist (bei Go-Projekten wird z. B. gofmt ausgeführt).


Styleguides einhalten: Halte dich an vereinbarte Styleguides. In JavaScript verwenden wir z. B. doppelte Anführungszeichen und Tabs zur Einrückung. Achte bei Python-Code auf PEP8-konformen Stil (4 Leerzeichen pro Einrückung, angemessene Zeilenlängen etc.).


Linter/Formatter einsetzen: Verwende für konsistenten Stil die projektweiten Linter/Formatter. Bei Bedarf stehen dafür Skripte oder npm-Scripts zur Verfügung (z. B. npm run lint:fix für JavaScript/TypeScript oder entsprechende Makefile-Targets).

Build-, Test- und Lint-Workflows


Build: Baue das Projekt lokal mit make build (falls vorhanden) oder den projektspezifischen Befehlen (z. B. npm run build bei Node.js, yarn build oder docker build für Container). Stelle sicher, dass der Build ohne Fehler durchläuft.


Test: Führe alle Tests aus (z. B. make test, pytest für Python-Tests, npm test für JavaScript). Neue oder geänderte Funktionalität sollte durch entsprechende Unit-Tests abgedeckt werden.


Lint: Starte statische Code-Prüfer (z. B. make lint oder npm run lint) und behebe gefundene Probleme. Unser CI schlägt fehl, wenn Linting-Fehler vorhanden sind.


Docker (optional): Falls Containerisierung vorgesehen ist, baue die Docker-Images (siehe Dockerfile) und nutze docker-compose bei Bedarf, um Abhängigkeiten (Datenbanken, Services) für Integrationstests bereitzustellen.


CI: Vor dem Merge führt die Continuous-Integration-Pipeline (GitHub Actions) alle Checks aus – Build, Linting und Tests müssen grün sein. Ein vollständiger CI-Durchlauf kann lokal mit make ci getestet werden (führt Formatierung, Build, Lint und Tests in einem Schritt aus).


Pull Requests, Code Reviews und CI-Prozess


Branching & PR-Erstellung: Entwickle Änderungen in eigenen Branches und öffne Pull Requests (kein Direkt-Push auf main). Beschreibe im PR klar, was geändert wurde und warum – referenziere ggf. die zugehörige Issue oder das Jira-Ticket.


Code Review: Jeder PR wird einem Code Review unterzogen. Mindestens ein Teammitglied muss den PR freigeben, bevor er gemergt wird. Commit-Nachrichten sollten prägnant sein und den Zweck der Änderung vermitteln (z. B. im Imperativ mit Ticket-Referenz). Nutze Draft PRs, wenn die Änderung noch nicht fertig ist, und markiere den PR als bereit zur Überprüfung, sobald die Umsetzung vollständig und lokal getestet ist.


Review-Kommentare: Feedback von Reviewern wird vom KI-Agenten ausgewertet. Sobald Kommentare von berechtigten Nutzern gepostet werden, liest Copilot diese und nimmt ggf. Code-Anpassungen vor. Der Agent geht die Anmerkungen nacheinander durch und aktualisiert den PR iterativ, bis alle angesprochenen Punkte behoben sind und der Code den Anforderungen entspricht. Reviewer sollten nach Möglichkeit mehrere Anmerkungen gebündelt in einem Review abgeben (statt vieler einzelner Kommentare), damit Copilot effizient darauf reagieren kann.


Merge: Führe den Merge des PR erst durch, wenn alle CI-Checks erfolgreich sind (automatisierter Build, Tests und Linter sind grün). Der KI-Agent stellt durch eigenes Testen sicher, dass die Änderungen die Akzeptanzkriterien erfüllen, was zu stabileren Pull Requests führt.


Projektstruktur


Unser Repository folgt einer klaren Struktur. Wichtige Verzeichnisse sind u.a.:


src/ – Hauptquellcode der Anwendung oder Services. Hier befindet sich die Kern-Implementierung der App bzw. des Produkts.


lib/ – Wiederverwendbare Bibliotheken, Module oder gemeinsam genutzter Code. Code in lib/ kann von src/ oder anderen Teilen genutzt werden (ggf. auch generierter Code oder Build-Artefakte bei bestimmten Sprachprojekten).


tests/ – Automatisierte Tests (Unit-Tests, Integrationstests etc.) sowie Testdaten und Fixtures. Neue Features oder Bugfixes sollten durch Tests in diesem Ordner abgedeckt werden.


docs/ – Dokumentation des Projekts. Hier liegen z. B. Anleitungen zur Einrichtung, Architekturübersichten, Changelogs und sonstige Markdown-Dokumente. Änderungen an öffentlichen APIs oder wichtigen Logiken sollten hier dokumentiert werden.


scripts/ – Hilfsskripte für Build, Deployment, Datenmigrationen oder andere Wartungsaufgaben. Diese Skripte automatisieren wiederkehrende Aufgaben (z. B. scripts/setup_dev_env.sh für die lokale Einrichtung).


config/ – Konfigurationsdateien und Vorlagen. Enthält z. B. Einstellungen für Umgebungen, YAML/JSON-Konfigurationen, Logging- oder CI-Konfigurationen.


.github/ – GitHub-spezifische Dateien (z. B. Actions-Workflows, Issue-Templates und diese Copilot-Instruktionsdatei). Unsere CI-Pipelines sind in .github/workflows/ definiert.


Verhaltensregeln für Copilot und ChatGPT


Klare Aufgabenumsetzung: Verstehe jede Aufgabe präzise und erfülle sie genau nach Beschreibung. Konzentriere dich auf die definierten Anforderungen und Akzeptanzkriterien – löse keine ungenstellten Probleme und halte den Umfang einer Issue möglichst klein und klar abgegrenzt.


Einhaltung von Standards: Befolge die vorgegebenen Code-Standards und Best Practices des Projekts (z. B. Sprachkonventionen, Design-Patterns) und erhalte die bestehende Projektstruktur aufrecht. Füge neuen Code in passende Module/Dateien ein und orientiere dich am Stil des bestehenden Codes, um Konsistenz zu wahren.


Änderungen begründen: Erkläre deine Änderungen verständlich. Nutze aussagekräftige Commit-Nachrichten und Pull-Request-Beschreibungen, um Was und Warum der Änderung zu erläutern. Bei Code-Reviews reagierst du konstruktiv auf Feedback und passt den Code gegebenenfalls an, anstatt Änderungen ungefragt zu verwerfen.


Tests schreiben: Stelle sicher, dass für neue Funktionen oder Bugfixes entsprechende Unit-Tests erstellt oder angepasst werden. Erhöhe die Testabdeckung, wann immer es sinnvoll ist. Tests sollten automatisiert im CI laufen und den Erfolg bzw. Misserfolg der Änderung validieren.


Sicherheitsbewusstsein: Achte darauf, keine Sicherheitslücken oder sensiblen Daten einzubringen. Befolge Best Practices für sichere Programmierung (z. B. Eingaben validieren, nur sichere SQL-Queries mit Platzhaltern nutzen, Fehlerausgaben auf das Nötige beschränken). Wenn du potenzielle Sicherheitsprobleme erkennst, markiere sie oder schlage sicherere Lösungen vor.


Dokumentation und Kommentare: Dokumentiere wichtige Änderungen, öffentliche APIs und komplexe Logik. Ergänze bei Bedarf Kommentare im Code für schwer verständliche Stellen. Wenn sich durch deine Änderung die Nutzung des Systems ändert oder ein größeres Feature hinzukommt, passe die Projektdokumentation im docs/-Verzeichnis an (z. B. Beschreibung, Beispiele oder Changelog-Einträge hinzufügen).


Erweiterte Funktionen: Abhängigkeiten & MCP


für fortgeschrittene Einstellungen und Fähigkeiten der KI-Agenten


Umgang mit Abhängigkeiten: Der KI-Agent arbeitet in einer isolierten, temporären Entwicklungsumgebung (bereitgestellt über GitHub Actions) und kann dort Code bauen sowie Tests und Linter ausführen. Stelle sicher, dass vor Testausführungen alle erforderlichen Abhängigkeiten installiert sind (z. B. via npm install, yarn oder pip install -r requirements.txt). Falls der Agent neue Bibliotheken benötigt, füge diese in den entsprechenden Dependency-Dateien (etwa package.json oder requirements.txt) hinzu und begründe die Notwendigkeit in der PR-Beschreibung. Um die Agent-Umgebung schneller startklar zu machen, können wir eine optionale Konfigurationsdatei copilot-setup-steps.yml definieren, die wichtige Abhängigkeiten vorab installiert.


Model Context Protocol (MCP): Für erweiterte Fähigkeiten kann der Copilot Coding Agent das MCP nutzen. Darüber kann er autonom bestimmte Tools verwenden (sogenannte MCP-Server), um zusätzliche Kontexte oder Aktionen einzubeziehen. Beispielsweise ermöglicht der eingebaute GitHub-MCP-Server dem Agenten schreibgeschützten Zugriff auf GitHub-Daten unseres Repositories, wie Issues und Pull Requests. Aktuell sind nur lokale MCP-Server konfiguriert, d. h. das Ausführen definierter Tools im GitHub-Actions-Container. Beachte: Das Aktivieren weiterer (externer) MCP-Server kann Performance oder Ergebnisqualität beeinflussen. Zusätzliche Tools sollten nur gezielt eingesetzt werden, wenn der Nutzen klar überwiegt. Standardmäßig ist der GitHub-MCP aktiv; andere Tools (z. B. Browser via Playwright-MCP, Sentry-MCP etc.) müssen explizit eingerichtet werden und sollten sparsam sowie verantwortungsvoll genutzt werden.
Quellenangaben


Adding repository custom instructions for GitHub Copilot – GitHub Docs (Anleitung zum Hinterlegen von Repository-spezifischen Copilot-Instruktionen)
GitHub


Best practices for using Copilot to work on tasks – GitHub Docs (Empfehlungen für effektives Arbeiten mit dem Copilot Coding Agent)
GitHub
GitHub


Extending Copilot coding agent with the Model Context Protocol (MCP) – GitHub Docs (Erläuterung des Model Context Protocol zur Erweiterung von Copilot)
GitHub

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
