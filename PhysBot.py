import logging

import discord
from discord.ext import commands
from snapcogs import Bot

import config


def main():
    intents = discord.Intents.all()
    allowed_mentions = discord.AllowedMentions(replied_user=False)

    startup_extensions = [
        "cogs.memes",
        "cogs.physum",
        "cogs.games",
        "cogs.Moderation",
        "cogs.TeX",
        "cogs.WolframAlpha",
        "cogs.Voice",
        "snapcogs.Admin",
        "snapcogs.Information",
        "snapcogs.Fun",
    ]

    bot = Bot(
        description="Bot pour le serveur Discord de la PHYSUM!",
        command_prefix=["p.", "P."],
        help_command=commands.DefaultHelpCommand(dm_help=False),
        activity=discord.Game(name="aider la Physum"),
        intents=intents,
        allowed_mentions=allowed_mentions,
        db_name="db/physbot.db",
        startup_extensions=startup_extensions,
    )

    bot.run(config.token, log_level=logging.WARNING)


if __name__ == "__main__":
    main()
