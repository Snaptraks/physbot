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

            await self.load_persistent_views()
            self.persistent_views_added = True

    @commands.has_guild_permissions(manage_roles=True)
    @commands.group()
    async def roles(self, ctx):
        """Commands to create and manage role selection menus."""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @roles.command(name="select")
    async def roles_select(self, ctx, *, flags: RolesFlags):
        """Create a role selection menu, to select many roles from the list."""

        view = views.RolesView(flags.roles)
        await flags.channel.send(flags.content, view=view)

    @roles.command(name="toggle")
    async def roles_toggle(self, ctx, *, flags: RolesFlags):
        """Create a role toggle menu, to select only one role from the list."""

        view = views.RolesToggleView(flags.roles)
        await flags.channel.send(flags.content, view=view)

    @roles.command(name="add")
    async def roles_add(self, ctx):
        """Add a role to the selection list."""

        pass

    @roles.command(name="delete")
    async def roles_delete(self, ctx):
        """Delete a role from the selection list."""

        pass

    async def load_persistent_views(self):
        print("loading views")
        for view in await self._get_views():
            guild = self.bot.get_guild(view["guild_id"])

            # get the roles
            roles = [
                guild.get_role(row["role_id"])
                for row in await self._get_roles(view["view_id"])
            ]

            # get the components id
            components_id = {
                row["name"]: row["component_id"]
                for row in await self._get_components(view["view_id"])
            }

            if view["view_type"] == "select":
                view_type = views.RolesView

            elif view["view_type"] == "toggle":
                view_type = views.RolesToggleView

            self.bot.add_view(
                view_type(roles, components_id=components_id),
                message_id=view["message_id"],
            )

    @tasks.loop(count=1)
    async def _create_tables(self):
        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS roles_view(
                guild_id   INTEGER NOT NULL,
                message_id INTEGER NOT NULL UNIQUE,
                view_id    INTEGER NOT NULL PRIMARY KEY,
                view_type  TEXT    NOT NULL
            )
            """
        )

        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS roles_component(
                component_id TEXT NOT NULL,
                name         TEXT NOT NULL,
                view_id      INTEGER NOT NULL,
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

    async def _get_views(self):
        async with self.bot.db.execute(
            """
            SELECT *
              FROM roles_view
            """
        ) as c:
            rows = await c.fetchall()

        return rows

    async def _get_roles(self, view_id):
        async with self.bot.db.execute(
            """
            SELECT *
              FROM roles_role
             WHERE view_id=:view_id
            """,
            dict(view_id=view_id),
        ) as c:
            rows = await c.fetchall()

        return rows

    async def _get_components(self, view_id):
        async with self.bot.db.execute(
            """
            SELECT *
              FROM roles_component
             WHERE view_id=:view_id
            """,
            dict(view_id=view_id),
        ) as c:
            rows = await c.fetchall()

        return rows
