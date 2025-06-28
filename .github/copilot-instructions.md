GitHub Copilot und ChatGPT Anweisungen
Dieses Repository nutzt GitHub Copilot (Codex) und ChatGPT (intern „MARCEL“ genannt) als unterstützende KI-Entwickler. Sie helfen beim Implementieren von Features, Reviewen von Code, Schreiben und Ausführen von Tests, Refactoring sowie Bugfixing. Die Nachverfolgung von Aufgaben erfolgt über Jira
docs.github.com
. Diese Anleitung stellt sicher, dass die KI-Agenten effektiv im Einklang mit unseren Entwicklungsstandards arbeiten. Bitte befolgen Sie die folgenden Richtlinien, damit Copilot und ChatGPT unsere Arbeitsabläufe optimal unterstützen.
Code-Formatierung und Stil
Führe vor jedem Commit das Formatierungstool aus (z. B. make fmt), um konsistente Code-Formatierung sicherzustellen
docs.github.com
. Dies stellt sicher, dass der Code einheitlich formatiert ist (bei Go-Projekten wird z. B. gofmt ausgeführt
docs.github.com
).
Halte dich an vereinbarte Styleguides: In JavaScript verwenden wir z. B. doppelte Anführungszeichen und Tabs zur Einrückung
docs.github.com
. Achte bei Python-Code auf PEP8-konformen Stil (4 Leerzeichen pro Einrückung, vernünftige Zeilenlängen usw.).
Verwende für konsistenten Stil projektweite Linter/Formatter. Bei Bedarf stehen dafür Skripte oder npm-Scripts zur Verfügung (z. B. npm run lint:fix für JavaScript/TypeScript oder entsprechende Makefile-Targets).
Build-, Test- und Lint-Workflows
Build: Baue das Projekt lokal mit make build (falls vorhanden) oder den projektspezifischen Befehlen (z. B. npm run build bei Node.js oder yarn build, docker build für Container)
docs.github.com
. Stelle sicher, dass der Build ohne Fehler durchläuft.
Test: Führe alle Tests aus (make test oder z. B. pytest für Python-Tests, npm test für JavaScript)
docs.github.com
. Neue oder geänderte Funktionalität sollte durch entsprechende Unit-Tests abgedeckt werden.
Lint: Starte statische Code-Prüfer (make lint oder z. B. npm run lint) und behebe gefundene Probleme. Unser CI läuft nur fehlerfrei durch, wenn keine Linting-Fehler vorhanden sind.
Docker: Falls eine Containerisierung vorgesehen ist, baue die Docker-Images (siehe Dockerfile) und nutze docker-compose bei Bedarf, um Abhängigkeiten (Datenbanken, Services) für Integrationstests bereitzustellen.
CI: Vor dem Merge führt die Continuous-Integration-Pipeline (GitHub Actions) alle Checks aus – Build, Linting und Tests müssen grün sein. Ein vollständiger CI-Durchlauf kann lokal mit make ci getestet werden (führt Formatierung, Build, Lint und Tests in einem Schritt aus)
docs.github.com
.
Pull Requests, Code Reviews und CI-Prozess
Entwickle Änderungen in eigenen Branches und öffne Pull Requests (kein Direkt-Push auf main). Beschreibe im PR klar, was geändert wurde und warum – referenziere ggf. die zugehörige Issue oder Jira-Ticket.
Jeder PR wird einem Code Review unterzogen. Mindestens ein Teammitglied muss den PR freigeben, bevor er gemergt wird. Commit-Nachrichten sollten prägnant sein und den Zweck der Änderung vermitteln (z. B. im Imperativ mit Ticket-Referenz).
Nutze Draft PRs, wenn die Änderung noch nicht fertig ist, und markiere den PR als bereit zur Überprüfung, sobald die Umsetzung vollständig und lokal getestet ist.
Review-Kommentare: Feedback von Reviewern wird vom KI-Agenten ausgewertet. Sobald Kommentare von berechtigten Nutzern gepostet werden, liest Copilot diese und nimmt ggf. Code-Anpassungen vor
docs.github.com
. Reviewer sollten nach Möglichkeit mehrere Anmerkungen gebündelt in einem Review abgeben, statt viele einzelne Kommentare, damit Copilot effizient darauf reagieren kann
docs.github.com
.
Merge den PR erst, wenn alle CI-Checks erfolgreich sind (automatisierter Build, Tests und Linter). Der KI-Agent stellt durch eigenes Testen sicher, dass die Änderungen die Akzeptanzkriterien erfüllen, was zu besseren Pull Requests führt
docs.github.com
.
Projektstruktur
Unser Repository folgt einer klaren Struktur. Wichtige Verzeichnisse sind:
src/ – Hauptquellcode der Anwendung oder Services. Hier befindet sich die Kern-Implementierung der App bzw. des Produkts.
lib/ – Wiederverwendbare Bibliotheken, Module oder gemeinsam genutzter Code. Code in lib/ kann von src/ oder anderen Teilen genutzt werden (ggf. auch generierter Code oder Build-Artefakte bei bestimmten Sprachprojekten).
tests/ – Automatisierte Tests (Unit-Tests, Integrationstests, etc.) sowie Testdaten und Fixtures. Neue Features oder Bugs sollten durch Tests in diesem Ordner abgedeckt werden.
docs/ – Dokumentation des Projekts. Hier liegen z. B. Anleitung zur Einrichtung, Architekturübersichten, Changelogs und sonstige Markdown-Dokumente. Änderungen an öffentlichen APIs oder wichtigen Logiken sollten hier dokumentiert werden.
scripts/ – Hilfsskripte für Build, Deployment, Datenmigrationen oder andere Wartungsaufgaben. Diese Scripts automatisieren wiederkehrende Aufgaben (z. B. scripts/setup_dev_env.sh für lokale Einrichtung).
config/ – Konfigurationsdateien und Vorlagen. Enthält z. B. Einstellungen für Umgebungen, YAML/JSON-Konfigurationen, Logging- oder CI-Konfigurationen.
.github/ – GitHub-spezifische Dateien (z. B. Actions-Workflows, Issue-Templates und diese Copilot-Instruktionsdatei). Unsere CI-Pipelines sind in .github/workflows/ definiert.
Verhaltensregeln für Copilot und ChatGPT
Klare Aufgabenumsetzung: Verstehe jede Aufgabe präzise und erfülle sie genau nach Beschreibung. Konzentriere dich auf die definierten Anforderungen und Akzeptanzkriterien
docs.github.com
 – löse keine ungestellten Probleme und halte den Umfang einer Issue möglichst klein und wohl definiert.
Einhaltung von Standards: Befolge die vorgegebenen Code-Standards und Best Practices des Projekts (z. B. Sprach-Konventionen, Design-Patterns) und erhalte die bestehende Projektstruktur aufrecht
docs.github.com
. Füge neuen Code in passende Module/Dateien ein und orientiere dich am Stil des bestehenden Codes, um Konsistenz zu wahren.
Änderungen begründen: Erkläre deine Änderungen verständlich. Nutze aussagekräftige Commit-Nachrichten und Pull-Request-Beschreibungen, um das Was und Warum der Änderung zu erläutern. Bei Code-Reviews reagierst du konstruktiv auf Feedback und passt den Code gegebenenfalls an, anstatt Änderungen ungefragt zu verwerfen.
Tests schreiben: Stelle sicher, dass für neue Funktionen oder Bugfixes entsprechende Unit-Tests erstellt oder angepasst werden. Erhöhe die Testabdeckung, wann immer es sinnvoll ist
docs.github.com
. Tests sollten automatisiert im CI laufen und Erfolg/Misserfolg der Änderung validieren.
Dokumentation und Kommentare: Dokumentiere wichtige Änderungen, öffentliche APIs und komplexe Logik. Ergänze bei Bedarf Kommentare im Code für schwer verständliche Stellen. Wenn sich durch deine Änderung die Nutzung des Systems ändert oder ein größeres Feature hinzukommt, passe die Projekt-Dokumentation im docs/-Verzeichnis an
docs.github.com
 (z. B. füge Beschreibung, Beispiele oder Changelog-Einträge hinzu).
Erweiterte Funktionen: Abhängigkeiten & MCP
(Optional – für fortgeschrittene Einstellungen und Fähigkeiten der KI-Agenten.)
Umgang mit Abhängigkeiten: Der KI-Agent arbeitet in einer isolierten, temporären Entwicklungsumgebung (bereitgestellt über GitHub Actions) und kann dort Code bauen sowie Tests und Linter ausführen
docs.github.com
. Stelle sicher, dass vor Testausführungen alle erforderlichen Abhängigkeiten installiert sind (z. B. via npm install, yarn oder pip install -r requirements.txt). Falls der Agent neue Bibliotheken benötigt, füge diese in den entsprechenden Dependency-Dateien (etwa package.json oder requirements.txt) hinzu und begründe die Notwendigkeit in der PR-Beschreibung. Um die Agent-Umgebung schneller startklar zu machen, können wir eine copilot-setup-steps.yml konfigurieren, die wichtige Abhängigkeiten vorab installiert
docs.github.com
.
Model Context Protocol (MCP): Für erweiterte Fähigkeiten kann der Copilot Coding Agent das MCP nutzen
docs.github.com
. Darüber kann er autonom bestimmte Tools verwenden (sogenannte MCP-Server), um zusätzliche Kontexte oder Aktionen einzubeziehen. Beispielsweise ermöglicht der eingebaute GitHub-MCP-Server dem Agenten schreibgeschützten Zugriff auf GitHub-Daten unseres Repositories, wie Issues und Pull Requests
docs.github.com
. Aktuell sind nur lokale MCP-Server konfiguriert, d. h. das Ausführen definierter Tools im GitHub Actions Container. Beachte: Das Aktivieren weiterer (externer) MCP-Server kann die Performance oder Ergebnisqualität beeinflussen
docs.github.com
. Daher sollen zusätzliche Tools nur gezielt eingesetzt werden, wenn der Nutzen klar überwiegt. Standardmäßig ist der GitHub-MCP aktiv; andere Tools (z. B. Browser via Playwright-MCP, Sentry-MCP etc.) müssen explizit eingerichtet werden und sollten sparsam und verantwortungsvoll genutzt werden.
Quellenangaben

Adding repository custom instructions for GitHub Copilot - GitHub Docs

https://docs.github.com/en/copilot/how-tos/custom-instructions/adding-repository-custom-instructions-for-github-copilot

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Best practices for using Copilot to work on tasks - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks

Extending Copilot coding agent with the Model Context Protocol (MCP) - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/extending-copilot-coding-agent-with-mcp

Extending Copilot coding agent with the Model Context Protocol (MCP) - GitHub Docs

https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/extending-copilot-coding-agent-with-mcp
Alle Quellen

docs.github
