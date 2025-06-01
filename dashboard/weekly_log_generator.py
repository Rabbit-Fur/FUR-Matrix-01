
import os
import sqlite3
import requests
from datetime import datetime, timedelta

DB_PATH = "data/admin_users.db"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
LOG_DIR = "core/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_markdown_report(participation, upcoming, filename):
    lines = [f"# 📊 Wöchentlicher Report – {datetime.utcnow().date()}\n"]

    lines.append("## 🏅 Top-Teilnehmer der Woche")
    for row in participation:
        lines.append(f"- `{row['user_id']}` – **{row['count']}x teilgenommen**")

    lines.append("\n## 🔮 Kommende Events")
    for event in upcoming:
        lines.append(f"- **{event['title']}** – `{event['event_time']}`")

    lines.append("\n[Zum Admin-Report im Web](/admin/weekly-report)")
    content = "\n".join(lines)

    with open(os.path.join(LOG_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)

    return content

def send_webhook(content):
    if not WEBHOOK_URL:
        print("⚠️ Kein DISCORD_WEBHOOK_URL gesetzt.")
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": content[:1900]})
    except Exception as e:
        print(f"❌ Webhook-Fehler: {e}")

def run_weekly_log():
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)
    week_end = now + timedelta(days=7)

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT user_id, COUNT(*) as count
        FROM event_participants
        JOIN events ON event_participants.event_id = events.id
        WHERE datetime(events.event_time) BETWEEN ? AND ?
        GROUP BY user_id ORDER BY count DESC
    """, (week_start.isoformat(), now.isoformat()))
    participation = cur.fetchall()

    cur.execute("""
        SELECT id, title, event_time
        FROM events
        WHERE datetime(event_time) BETWEEN ? AND ?
        ORDER BY event_time
    """, (now.isoformat(), week_end.isoformat()))
    upcoming = cur.fetchall()
    db.close()

    filename = f"{now.date()}-weekly.md"
    markdown = generate_markdown_report(participation, upcoming, filename)
    send_webhook(markdown)
    print(f"✅ Weekly log created: {filename}")

if __name__ == "__main__":
    run_weekly_log()
