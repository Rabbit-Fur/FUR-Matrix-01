"""Simple inbox handler for Discord DMs and feedback messages."""

from datetime import datetime
import logging
from pymongo.errors import PyMongoError


log = logging.getLogger(__name__)


class InboxAgent:
    """Persist incoming messages to the inbox collection."""

    def __init__(self, db):
        self.db = db

    def receive_message(self, discord_id: str, content: str):
        """Store a message from a Discord user.

        Parameters
        ----------
        discord_id: str
            Identifier of the Discord user sending the message.
        content: str
            Text content of the message.

        Returns
        -------
        str
            Confirmation message for the user.

        Raises
        ------
        ValueError
            If ``content`` is empty.
        PyMongoError
            If the database operation fails.
        """

        if not content:
            raise ValueError("content must not be empty")

        try:
            self.db["inbox"].insert_one(
                {
                    "discord_id": discord_id,
                    "message": content,
                    "timestamp": datetime.utcnow(),
                }
            )
        except PyMongoError:
            log.exception("Failed to store message for %s", discord_id)
            raise

        return "📥 Nachricht empfangen – danke für dein Feedback!"
