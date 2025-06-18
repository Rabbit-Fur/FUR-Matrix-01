"""
ChampionAgent – generiert Poster, speichert Hall-of-Fame und triggert Discord-Webhook
"""
class ChampionAgent:
    def __init__(self, db):
        self.db = db

    def generate_monthly_poster(self, champion_data):
        # Poster + Webhook-Upload
        pass

    def insert_champion_entry(self, data):
        self.db["hall_of_fame"].insert_one(data)
