import asyncio

import discord
from discord import app_commands

from bot.translator import MyTranslator
from fur_lang import i18n


def test_translator_command_name():
    translator = MyTranslator()
    i18n.translations = {"en": {"cmd_ping_name": "ping"}, "de": {"cmd_ping_name": "ping"}}
    ctx = app_commands.TranslationContext(
        location=app_commands.TranslationContextLocation.command_name,
        data=None,
    )
    result = asyncio.run(
        translator.translate(app_commands.locale_str("cmd_ping_name"), discord.Locale.german, ctx)
    )
    assert result == "ping"
