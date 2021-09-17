from datetime import datetime

import discord
from discord.ext import commands
import asyncpraw

import config


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = None

    @commands.Cog.listener()
    async def on_ready(self):
        if self.reddit is None:
            self.reddit = asyncpraw.Reddit(
                client_id=config.reddit_client_id,
                client_secret=config.reddit_client_secret,
                username=config.reddit_username,
                password=config.reddit_password,
                user_agent=(
                    f"python:{self.bot.user.name}:v0.1.0 "
                    f"(by u/{config.reddit_username})"
                ),
                requestor_kwargs={"session": self.bot.http_session},
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        if "<:ripsimon:768530426884915272>" in message.content:
            await message.add_reaction("<:faridsus:768530389685764127>")

        if message.author.name == "Hassan":
            await message.add_reaction("<:crottesulcoeur:751234270781112420>")

        for forbidden_word in ["ingénieur", "elon musk", "pi=3"]:
            if forbidden_word in message.content.lower():
                await message.add_reaction("\U0001f4a9")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction) == "<:ripsimon:768530426884915272>":
            await reaction.message.add_reaction("<:faridsus:768530389685764127>")

    @commands.command()
    async def meme(self, ctx, *, subreddit_name="physicsmemes"):
        """Trouve un meme sur le subreddit mentionné
        (par défaut sur r/physicsmemes)
        """
        subreddit = await self.reddit.subreddit(subreddit_name.lower())
        await subreddit.load()
        submission = await subreddit.random()
        await submission.author.load()

        if subreddit.over18 or submission.over_18:
            # we don't want NSFW posts here
            print(f"Someone tried to look at NSFW memes:\n{submission.url}")
            return await ctx.reply("https://i.redd.it/cah38y4p41f51.png")

        embed = discord.Embed(
            color=0xFF4500,
            title=submission.title,
            url=f"https://www.reddit.com{submission.permalink}",
            description=submission.selftext,
            timestamp=datetime.utcfromtimestamp(submission.created_utc),
        ).set_image(
            url=submission.url,
        ).set_author(
            name=submission.author.name,
            url=f"https://www.reddit.com/u/{submission.author.name}",
            icon_url=submission.author.icon_img,
        ).set_footer(
            text="  •  ".join([
                f"{submission.score} points",
                f"{submission.num_comments} comments",
                "Published on",
            ]),
        )

        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Memes(bot))
