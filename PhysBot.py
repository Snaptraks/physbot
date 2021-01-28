import aiosqlite
import aiohttp
import discord
from discord.ext import commands

import config

__version__ = "0.2"


async def create_http_session(loop):
    """Create an async HTTP session. Required to be from an async function
    by aiohttp>=3.5.4
    """
    return aiohttp.ClientSession(loop=loop)


async def create_db_connection(db_name):
    """Create the connection to the database."""

    return await aiosqlite.connect(
        db_name, detect_types=1)  # 1: parse declared types


class PhysBot(commands.Bot):
    """Subclass of the commands.Bot class.
    This is helpful when adding attributes to the bot such as a
    database connection or http session.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create HTTP session
        self.http_session = self.loop.run_until_complete(
            create_http_session(self.loop))

        # Make DB connection, save in memory if no name is provided
        self.db = self.loop.run_until_complete(
            create_db_connection(kwargs.get('db_name', ':memory:')))
        # allow for name-based access of data columns
        self.db.row_factory = aiosqlite.Row

    async def close(self):
        """Close the DB connection and HTTP session."""

        await self.http_session.close()
        await self.db.close()
        await super().close()

    async def on_ready(self):
        print(
            f"Logged in as {self.user.name} (ID:{self.user.id})\n"
            f"Connected to {len(self.guilds)} guilds\n"
            f"Connected to {len(set(self.get_all_members()))} users\n"
            "--------\n"
            f"Current Discord.py Version: {discord.__version__}\n"
            "--------"
        )


if __name__ == '__main__':

    intents = discord.Intents.all()
    allowed_mentions = discord.AllowedMentions(replied_user=False)

    bot = PhysBot(
        description="Bot pour le serveur Discord de la PHYSUM!",
        command_prefix=["p.", "P."],
        activity=discord.Game(name="aider la Physum"),
        intents=intents,
        allowed_mentions=allowed_mentions,
        db_name='db/physbot.db',
    )

    startup_extensions = [
        'cogs.admin',
        'cogs.memes',
        'cogs.physum',
        'cogs.information',
        'cogs.games',
        'cogs.TeX',
        'cogs.WolframAlpha',
    ]

    for extension in startup_extensions:
        bot.load_extension(extension)

    bot.run(config.token)
