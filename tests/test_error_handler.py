import asyncio
import logging

import discord
from discord.ext import commands

from bot.cogs.error_handler import ErrorHandler
from fur_lang.i18n import t


class DummyResponse:
    def __init__(self):
        self.message = None
        self._done = False

    async def send_message(self, message, ephemeral=False):
        self._done = True
        self.message = message

    def is_done(self):
        return self._done


class DummyFollowup:
    def __init__(self):
        self.message = None

    async def send(self, message, ephemeral=False):
        self.message = message


class DummyInteraction:
    def __init__(self):
        self.user = type("User", (), {"id": 1})()
        self.response = DummyResponse()
        self.followup = DummyFollowup()


def run(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def test_missing_permissions_message():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
    handler = ErrorHandler(bot)
    interaction = DummyInteraction()

    run(handler.on_application_command_error(interaction, commands.MissingPermissions(["admin"])))

    expected = t("error_missing_permissions", default="🚫 Missing permissions.", lang="de")
    assert interaction.response.message == expected


def test_command_invoke_error_logs(caplog):
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
    handler = ErrorHandler(bot)
    interaction = DummyInteraction()

    with caplog.at_level(logging.ERROR):
        run(
            handler.on_application_command_error(
                interaction, commands.CommandInvokeError(Exception("boom"))
            )
        )

    expected = t("error_default_message", default="An error occurred.", lang="de")
    assert interaction.response.message == expected
    assert "CommandInvokeError" in caplog.text
