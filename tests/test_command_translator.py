import asyncio

import discord
from discord import app_commands

from bot.translator import MyTranslator


def test_translator_command_name():
    translator = MyTranslator()
    ctx = app_commands.TranslationContext(
        location=app_commands.TranslationContextLocation.command_name,
        data=None,
    )
    result = asyncio.run(
        translator.translate(app_commands.locale_str("cmd_ping_name"), discord.Locale.german, ctx)
    )
    assert result == "ping"
