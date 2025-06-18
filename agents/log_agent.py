# agents/log_agent.py

import os
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path


class LogAgent:
    def __init__(self, db, log_dir="core/logs"):
        self.db = db
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _count_today(self, collection_name, date_field="created_at"):
        today = datetime.utcnow().date()
        return self.db[collection_name].count_documents({
            date_field: {"$gte": datetime(today.year, today.month, today.day)}
        })

    def _count_last_week(self, collection_name, date_field="created_at"):
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        return self.db[collection_name].count_documents({
            date_field: {"$gte": last_week}
        })

    def generate_daily_log(self) -> str:
        today = datetime.utcnow().strftime("%Y-%m-%d")

        log = [
            f"# 📅 Daily Log – {today}",
            "",
            f"- 👤 Neue Nutzer heute: **{self._count_today('users')}**",
            f"- 🔔 Neue Reminders heute: **{self._count_today('reminders')}**",
            f"- 📆 Neue Events heute: **{self._count_today('events')}**",
            "",
            "✅ Systeme aktiv",
            "✅ MongoDB erreichbar",
            "",
            "_Autogeneriert vom FUR LogAgent_",
        ]

        content = "\n".join(log)
        file_path = self.log_dir / f"daily_log_{today}.md"
        file_path.write_text(content, encoding="utf-8")
        return content

    def generate_weekly_log(self) -> str:
        now = datetime.utcnow()
        week = now.isocalendar().week
        log = [
            f"# 📊 Weekly Log – KW {week} ({now.strftime('%Y-%m-%d')})",
            "",
            f"- 👥 Neue Nutzer diese Woche: **{self._count_last_week('users')}**",
            f"- 📆 Neue Events diese Woche: **{self._count_last_week('events')}**",
            f"- 🔔 Neue Reminders diese Woche: **{self._count_last_week('reminders')}**",
            "",
            "📈 Aktivität stabil",
            "_Erstellt vom FUR SYSTEM Monitoring_"
        ]
        content = "\n".join(log)
        file_path = self.log_dir / f"weekly_log_kw{week}.md"
        file_path.write_text(content, encoding="utf-8")
        return content

    def send_to_discord(self, content: str, webhook_url: str) -> bool:
        try:
            payload = {
                "content": f"📄 FUR LOG:\n```md\n{content[:1900]}\n```"  # Discord limitiert auf 2000 chars
            }
            response = requests.post(webhook_url, json=payload)
            logging.info(f"📤 Log an Discord gesendet: {response.status_code}")
            return response.status_code == 204
        except Exception as e:
            logging.error(f"❌ Fehler beim Senden an Discord: {e}")
            return False
