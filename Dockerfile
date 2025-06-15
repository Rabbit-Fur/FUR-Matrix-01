FROM python:3.11-slim

# 🔧 Installiere git für pip git+... Support
RUN apt-get update \
 && apt-get install -y git \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 📁 Setze Arbeitsverzeichnis
WORKDIR /app

# 📦 Installiere Python-Abhängigkeiten
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 🧩 Kopiere restliche App-Dateien
COPY . .

# 🚀 Starte Flask-App
CMD ["python", "main_app.py"]
