import discord
from discord.ext import commands
from . import views


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.persistent_views_added = True

    @commands.command()
    async def roles(self, ctx, roles: commands.Greedy[discord.Role]):
        view = views.RolesView(roles)
        await ctx.send("roles", view=view)
