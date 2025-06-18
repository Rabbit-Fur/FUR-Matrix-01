"""
MonitoringAgent – sammelt System-Status, Fehler-Logs und Healthchecks für das FUR-System
"""

import requests
import logging
from datetime import datetime

class MonitoringAgent:
    def __init__(self, health_url="http://localhost:8080/health", timeout=3):
        self.health_url = health_url
        self.timeout = timeout
        self.last_check = None
        self.last_status = None
        self.last_response = None

    def check_system(self) -> bool:
        """Führt einen Healthcheck durch und cached das Ergebnis"""
        try:
            response = requests.get(self.health_url, timeout=self.timeout)
            self.last_check = datetime.utcnow()
            self.last_status = response.ok
            self.last_response = response.text
            logging.info(f"📡 Healthcheck {self.last_check}: {response.status_code}")
            return response.ok
        except requests.RequestException as e:
            self.last_check = datetime.utcnow()
            self.last_status = False
            self.last_response = str(e)
            logging.error(f"❌ Monitoring-Fehler: {e}")
            return False

    def get_status(self) -> dict:
        """Liefert den aktuellen Status als Dictionary"""
        return {
            "checked_at": self.last_check,
            "status_ok": self.last_status,
            "raw_response": self.last_response
        }
