import mongomock
from agents.inbox_agent import InboxAgent
from datetime import datetime


def test_receive_message_stores_document():
    client = mongomock.MongoClient()
    db = client["testdb"]
    agent = InboxAgent(db)

    discord_id = "12345"
    content = "Hello there"

    agent.receive_message(discord_id, content)

    doc = db["inbox"].find_one({"discord_id": discord_id})
    assert doc is not None
    assert doc["discord_id"] == discord_id
    assert doc["message"] == content
    assert "timestamp" in doc
    assert isinstance(doc["timestamp"], datetime)
