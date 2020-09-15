import discord
from discord.ext import commands
import json
import random


class Physum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('physics_quotes.json') as f:
            self.quotes = json.load(f)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = discord.utils.get(guild.channels, name="rôles")
        if guild.system_channel is not None:
            to_send = (
                f'Bienvenue {member.mention} dans le serveur de la Physum!\n'
                f'Choisis ton année et ton programme dans {channel.mention} '
                'pour avoir accès à plus de salons et de fun :) '
            )
            await guild.system_channel.send(to_send)

    @commands.Cog.listener(name='on_message')
    async def quote(self, message):
        """Provide a random physics quote when mentionned."""

        if (self.bot.user.mentioned_in(message)
                and not message.mention_everyone
                and not message.content.startswith(self.bot.command_prefix)):

            quote = random.choice(self.quotes)
            content = f"{quote['text']}\n — *{quote['author']}*"

            await message.channel.send(content)


def setup(bot):
    bot.add_cog(Physum(bot))
