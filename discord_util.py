from utils.discord_util import *  # noqa


class Client:
    """Minimal stub to satisfy bot import."""



class Intents:
    @staticmethod
    def all():
        return Intents()

    message_content = True
    guilds = True
    members = True
