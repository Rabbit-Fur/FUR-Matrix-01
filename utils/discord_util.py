"""
discord_util.py – Minimaler Discord.py-Stub für Tests und Offline-Entwicklung

Stellt Dummy-Implementierungen der wichtigsten discord.py-Klassen bereit,
um die Integration in Testumgebungen und Offline-Entwicklung zu ermöglichen.
"""


class Client:
    """Stub für discord.Client (Testumgebung)."""

    def __init__(self, *args, **kwargs):
        self.user = None

    async def start(self, *args, **kwargs):
        """Simuliert das Starten des Bots."""
        print("🧪 Stub-Client gestartet")

    async def close(self):
        """Simuliert das Schließen des Bots."""
        print("🧪 Stub-Client geschlossen")

    def run(self, token: str):
        """Simuliert den Run-Aufruf mit Token."""
        print(f"🧪 run(token={token}) aufgerufen (stub)")

    def is_ready(self) -> bool:
        """Immer bereit (Mock)."""
        return True


class Intents:
    """Stub für discord.Intents."""

    @classmethod
    def default(cls):
        """Gibt ein Default-Intents-Objekt zurück."""
        return cls()

    @classmethod
    def all(cls):
        """Gibt ein Intents-Objekt mit allen Berechtigungen zurück."""
        return cls()


class Message:
    """Stub für discord.Message."""

    def __init__(self, content: str = "", author=None):
        self.content = content
        self.author = author


class User:
    """Stub für discord.User."""

    def __init__(self, name: str = "StubUser"):
        self.name = name
        self.id = 1234
