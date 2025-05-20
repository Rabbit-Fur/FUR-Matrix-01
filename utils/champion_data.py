
# champion_data.py

from datetime import datetime

champions = [
    {
        "username": "Xevi",
        "honor_title": "🔥 Champion of the Month 🔥",
        "month": "Mai 2025",
        "poster_url": "/static/champions/xevi_april2025.png",
        "created_at": datetime.utcnow().isoformat()
    }
]

def get_latest_champion():
    return champions[-1] if champions else None
