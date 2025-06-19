"""
AuthAgent – prüft Discord-Login, Rollen, Berechtigungen
"""
class AuthAgent:
    def __init__(self, session, db):
        self.session = session
        self.db = db

    def get_user_role(self, discord_id):
        user = self.db["users"].find_one({"discord_id": discord_id})
        return user.get("role_level") if user else None

    def has_admin_access(self, discord_id):
        return self.get_user_role(discord_id) == "admin"
