"""Minimal pytest configuration for health check tests."""

import os
import pymongo
import mongomock

# Dummy environment variables required by Config
os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("DISCORD_TOKEN", "dummy")
os.environ.setdefault("DISCORD_GUILD_ID", "1")
os.environ.setdefault("REMINDER_CHANNEL_ID", "1")
os.environ.setdefault("DISCORD_CLIENT_ID", "1")
os.environ.setdefault("DISCORD_CLIENT_SECRET", "dummy")
os.environ.setdefault("DISCORD_REDIRECT_URI", "http://localhost/callback")
os.environ.setdefault("GOOGLE_CLIENT_ID", "gid")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "gsecret")
os.environ["MONGODB_URI"] = "mongodb://localhost:27017/testdb"
os.environ.setdefault("SESSION_LIFETIME_MINUTES", "60")
os.environ.setdefault("R3_ROLE_IDS", "1")
os.environ.setdefault("R4_ROLE_IDS", "2")
os.environ.setdefault("ADMIN_ROLE_IDS", "3")

# Use in-memory MongoDB for tests
pymongo.MongoClient = mongomock.MongoClient
