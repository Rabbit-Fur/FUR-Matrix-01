import importlib

import mongomock

import fur_mongo
import mongo_service


def _reload_mongo_service(monkeypatch):
    monkeypatch.delenv("MONGODB_URI", raising=False)
    mod = importlib.reload(mongo_service)
    mod.client = mongomock.MongoClient()
    mod.db = mod.client["testdb"]
    return mod


def _reload_fur_mongo(monkeypatch):
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setattr("pymongo.MongoClient", mongomock.MongoClient)
    return importlib.reload(fur_mongo)


def test_mongo_service_import_without_uri(monkeypatch):
    mod = _reload_mongo_service(monkeypatch)
    assert mod.MONGO_URI == "mongodb://localhost:27017/FURdb"


def test_fur_mongo_import_without_uri(monkeypatch):
    mod = _reload_fur_mongo(monkeypatch)
    assert mod.MONGO_URI == "mongodb://localhost:27017/FURdb"
