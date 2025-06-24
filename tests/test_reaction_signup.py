import asyncio
import types

from bson import ObjectId

import bot.cogs.reaction_signup as rs_mod


class DummyMessage:
    def __init__(self, content):
        self.content = content


class DummyChannel:
    async def fetch_message(self, message_id):
        return DummyMessage("Event [ID:507f1f77bcf86cd799439011]")


class DummyBot:
    def get_channel(self, cid):
        return DummyChannel()


class DummyCollection(list):
    def find_one(self, query):
        if query.get("_id"):
            return {"_id": query["_id"]}
        return None

    def update_one(self, flt, update, upsert=False):
        self.append(flt)


def test_reaction_signup(monkeypatch):
    events_col = DummyCollection()
    participants_col = DummyCollection()

    def get_coll(name):
        return {"events": events_col, "event_participants": participants_col}[name]

    monkeypatch.setattr(rs_mod, "get_collection", get_coll)

    bot = DummyBot()
    cog = rs_mod.ReactionSignup(bot)

    class DummyEmoji:
        def __str__(self):
            return "🔥"

    payload = types.SimpleNamespace(
        emoji=DummyEmoji(),
        channel_id=1,
        message_id=2,
        user_id=123,
    )

    asyncio.run(cog.on_raw_reaction_add(payload))

    assert participants_col[0] == {
        "event_id": ObjectId("507f1f77bcf86cd799439011"),
        "user_id": "123",
    }
