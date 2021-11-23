import discord
from discord.ext import commands, tasks
from . import views


class RolesFlags(commands.FlagConverter):
    channel: discord.TextChannel = commands.flag(default=lambda ctx: ctx.channel)
    content: str = commands.flag(
        default="Select from the following roles:", aliases=["message"]
    )
    roles: tuple[discord.Role, ...]  # able to add more than one with the flag


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False
        self._create_tables.start()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.persistent_views_added = True

    @commands.command()
    async def select(self, ctx, *, flags: RolesFlags):
        view = views.RolesView(flags.roles)
        await flags.channel.send(flags.content, view=view)

    @commands.command()
    async def toggle(self, ctx, *, flags: RolesFlags):
        view = views.RolesToggleView(flags.roles)
        await flags.channel.send(flags.content, view=view)

    @tasks.loop(count=1)
    async def _create_tables(self):
        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS roles_view(
                guild_id   INTEGER NOT NULL,
                message_id INTEGER UNIQUE,
                view_id    INTEGER NOT NULL PRIMARY KEY
            )
            """
        )

        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS roles_component(
                component_id TEXT NOT NULL,
                name         TEXT NOT NULL,
                view_id INTEGER NOT NULL,
                FOREIGN KEY (view_id)
                    REFERENCES roles_view (view_id)
            )
            """
        )

        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS roles_role(
                role_id INTEGER NOT NULL,
                view_id INTEGER NOT NULL,
                FOREIGN KEY (view_id)
                    REFERENCES roles_view (view_id)
            )
            """
        )
