"""
base_commands.py – Basisbefehle für alle User (z. B. Ping, Info, Status)

Dieses Cog stellt grundlegende Commands bereit, die für alle Servermitglieder nutzbar sind.
"""

import discord
from discord.ext import commands


class BaseCommands(commands.Cog):
    """
    Cog: Basisbefehle für alle User.

    Enthält einfache Commands wie !ping (Status) und !fur (Allianz-Info).
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        """
        Befehl: !ping
        Antwortet mit einem Status-Check.

        Args:
            ctx (commands.Context): Aufruf-Kontext.
        """
        await ctx.send("🏓 Pong! FUR is online.")

    @commands.command(name="fur")
    async def fur_info(self, ctx: commands.Context) -> None:
        """
        Befehl: !fur
        Zeigt grundlegende Informationen zur FUR-Allianz an.

        Args:
            ctx (commands.Context): Aufruf-Kontext.
        """
        await ctx.send("🔥 Welcome to the FUR Alliance – Strength, Unity, Respect.")


async def setup(bot: commands.Bot) -> None:
    """
    Registriert das BaseCommands-Cog beim Bot.

    Args:
        bot (commands.Bot): Discord-Bot-Instanz.
    """
    await bot.add_cog(BaseCommands(bot))
