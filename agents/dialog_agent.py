"""
DialogAgent – verarbeitet Benutzer-Interaktionen (Discord & Web) kontextuell
"""


class DialogAgent:
    def __init__(self):
        pass

    def respond(self, message: str) -> str:
        if "hilfe" in message.lower():
            return "ℹ️ Du kannst Hilfe zu Events, Punkten oder Befehlen erhalten."
        return "🤖 Ich habe dich verstanden!"
