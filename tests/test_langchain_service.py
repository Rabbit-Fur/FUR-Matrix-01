import types  # noqa: F401

import pytest  # noqa: F401

import src.services.langchain_service as mod


class DummyEmbeddings:
    def embed_documents(self, texts):
        return [[0.0] * 3 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 3


def test_get_history(monkeypatch):
    captured = {}

    class FakeHistory:
        pass

    def fake_init(connection_string, session_id, database_name, collection_name):
        captured.update(
            {
                "uri": connection_string,
                "session_id": session_id,
                "db": database_name,
                "collection": collection_name,
            }
        )
        return FakeHistory()

    monkeypatch.setattr(mod, "MongoDBChatMessageHistory", fake_init)

    svc = mod.LangchainService(mongo_uri="uri", db_name="db")
    history = svc.get_history("sess")
    assert isinstance(history, FakeHistory)
    assert captured == {
        "uri": "uri",
        "session_id": "sess",
        "db": "db",
        "collection": "chat_history",
    }


def test_get_vector_store(monkeypatch):
    captured = {}

    class FakeStore:
        pass

    def fake_from_connection_string(uri, namespace, embedding):
        captured.update({"uri": uri, "ns": namespace, "embed": embedding})
        return FakeStore()

    monkeypatch.setattr(
        mod.MongoDBAtlasVectorSearch, "from_connection_string", fake_from_connection_string
    )

    emb = DummyEmbeddings()
    svc = mod.LangchainService(mongo_uri="uri", db_name="db")
    store = svc.get_vector_store(emb, namespace="ns")
    assert isinstance(store, FakeStore)
    assert captured["uri"] == "uri"
    assert captured["ns"] == "db.ns"
    assert captured["embed"] is emb
