import discord
from discord.ext import commands
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

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.persistent_views_added = True

    @commands.command()
    async def roles(self, ctx, *, flags: RolesFlags):
        view = views.RolesView(flags.roles)
        await flags.channel.send(flags.content, view=view)
