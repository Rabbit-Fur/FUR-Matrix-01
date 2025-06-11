"""Test package initialization for FUR System."""

import os

# Provide default values so configuration imports don't fail during test discovery.
os.environ.setdefault("DISCORD_TOKEN", "dummy")
os.environ.setdefault("DISCORD_GUILD_ID", "1")
os.environ.setdefault("DISCORD_CHANNEL_ID", "1")
