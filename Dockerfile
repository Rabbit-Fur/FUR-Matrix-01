# 🐍 Verwende ein minimales Python-Image
FROM python:3.11-slim

# 📁 Setze Arbeitsverzeichnis
WORKDIR /app

# 🛠️ Installiere System-Abhängigkeiten (inkl. git für flask-babel Installation)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# 📦 Installiere Python-Abhängigkeiten
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 🧩 Kopiere restliche App-Dateien
COPY . .

# 🚀 Starte die Anwendung
CMD ["python", "main_app.py"]
