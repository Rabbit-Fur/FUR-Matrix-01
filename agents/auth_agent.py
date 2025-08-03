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

    # ------------------------------------------------------------------
    # Session based helpers
    # ------------------------------------------------------------------
    def _current_role(self):
        return self.session.get("user", {}).get("role_level")

    def is_logged_in(self):
        """Return True if a user is present in session."""
        return "user" in self.session

    def is_r3(self):
        """Check if the current session user has at least R3 privileges."""
        return self._current_role() in {"R3", "R4", "ADMIN"}

    def is_r4(self):
        """Check if the current session user has at least R4 privileges."""
        return self._current_role() in {"R4", "ADMIN"}

    def is_admin(self):
        """Check if the current session user is an administrator."""
        return self._current_role() == "ADMIN"
