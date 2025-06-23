from __future__ import annotations

import discord
from discord import app_commands

from fur_lang.i18n import t


class MyTranslator(app_commands.Translator):
    """Simple translator using fur_lang.i18n.t."""

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext,
    ) -> str:
        key: str = string.extras.get("key", string.message)
        return t(key, default=string.message, lang=locale.value)
