from collections import defaultdict
from datetime import datetime

import discord
from discord.ext import commands, tasks
from discord.utils import parse_time

from . import menus


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self._create_tables.start()

    def cog_check(self, ctx):
        return commands.has_guild_permissions(
            administrator=True,
        ).predicate(ctx)

    # TODO: add deleted message log
    @commands.Cog.listener(name="on_raw_message_delete")
    async def log_deleted_message(self, payload):
        """Save when a message is deleted, in the database.
        Try to save as much information as possible.
        """
        if not payload.guild_id:
            # ignore DM messages
            return

        data = defaultdict(lambda: None)
        data.update({
            "channel_id": payload.channel_id,
            "guild_id": payload.guild_id,
            "message_id": payload.message_id,
            "deleted_at": datetime.utcnow(),
        })

        cached_message = payload.cached_message  # can be None
        if cached_message:
            data.update({
                "content": cached_message.clean_content,
                "user_id": cached_message.author.id,
                "jump_url": cached_message.jump_url,
            })

        await self._log_deleted_message(data)

    # TODO: add edited message log
    @commands.Cog.listener(name="on_raw_message_edit")
    async def log_edited_message(self, payload):
        """Save when a message is edited, in the database.
        Try to save as much information as possible.
        """
        if not payload.data.get("content"):
            # not a content edit
            return

        data = defaultdict(lambda: None)
        data.update({
            "channel_id": payload.channel_id,
            "message_id": payload.message_id,
            "edited_at": parse_time(payload.data.get("edited_timestamp")),
            "content_after": payload.data["content"],  # will always be present
            "guild_id": payload.data.get("guild_id"),
        })

        cached_message = payload.cached_message  # can be None
        if cached_message:
            data.update({
                "content_before": cached_message.clean_content,
                "user_id": cached_message.author.id,
                "jump_url": cached_message.jump_url,
            })

        await self._log_edited_message(data)

    # TODO: add user info command
    @commands.command(aliases=["user", "user_info", "member"])
    async def member_info(self, ctx, *, member: discord.Member = None):
        """Return info about a member."""

        if member is None:
            member = ctx.author

        embed = discord.Embed(
            title=str(member),
            color=discord.Color.blurple(),
        ).add_field(
            name="User information",
            value=(
                f"Created: {member.created_at}\n"
                f"Profile: {member.mention}\n"
                f"ID: {member.id}"
            ),
            inline=False,
        ).add_field(
            name="Member information",
            value=(
                f"Joined: {member.joined_at}\n"
                f"{len(member.roles)} roles"
            ),
            inline=False,
        ).set_thumbnail(
            url=member.avatar_url_as(format="png"),
        )

        await ctx.reply(embed=embed)

    # TODO: add command to get deleted messages
    @commands.group(invoke_without_command=True)
    async def deletelog(self, ctx):
        pass

    @deletelog.command(name="member")
    async def deletelog_member(self, ctx, member: discord.Member,
                               amount: int = 10):
        """Get the `amount` latest deleted messages of a member."""

        deleted_messages = await self._get_deleted_messages_member(
            member, amount)
        # pprint([m["deleted_at"] for m in deleted_messages])

        menu = menus.DeletedMessagesMenu(
            source=menus.DeletedMessagesSource(deleted_messages),
            clear_reactions_after=True,
        )
        await menu.start(ctx)

    @deletelog.command(name="channel")
    async def deletelog_channel(self, ctx, channel: discord.TextChannel,
                                amount: int = 10):
        """Get the `amount` latest deleted messages in a channel."""

        deleted_messages = await self._get_deleted_messages_channel(
            channel, amount)
        # pprint([m["deleted_at"] for m in deleted_messages])

        menu = menus.DeletedMessagesMenu(
            source=menus.DeletedMessagesSource(deleted_messages),
            clear_reactions_after=True,
        )
        await menu.start(ctx)

    # TODO: add command to get edited messages
    @commands.command()
    async def editlog(self, ctx, message: discord.Message):
        """Get the revisions of a message."""

    @tasks.loop(count=1)
    async def _create_tables(self):
        """Create the necessary tables, if they don't already exist."""

        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS moderation_deletelog(
                channel_id INTEGER   NOT NULL,
                guild_id   INTEGER   NOT NULL,
                message_id INTEGER   NOT NULL,
                deleted_at TIMESTAMP NOT NULL,
                content    TEXT,
                user_id    INTEGER,
                jump_url   TEXT
            )
            """
        )

        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS moderation_editlog(
                channel_id     INTEGER   NOT NULL,
                message_id     INTEGER   NOT NULL,
                edited_at      TIMESTAMP NOT NULL,
                guild_id       INTEGER,
                content_before TEXT,
                content_after  TEXT,
                user_id        INTEGER,
                jump_url       TEXT
            )
            """
        )

        await self.bot.db.commit()

    async def _log_deleted_message(self, data):
        """Save the deleted message to the DB."""

        await self.bot.db.execute(
            """
            INSERT INTO moderation_deletelog
            VALUES (:channel_id,
                    :guild_id,
                    :message_id,
                    :deleted_at,
                    :content,
                    :user_id,
                    :jump_url)
            """,
            data
        )

        await self.bot.db.commit()

    async def _log_edited_message(self, data):
        """Save the edited message to the DB."""

        await self.bot.db.execute(
            """
            INSERT INTO moderation_editlog
            VALUES (:channel_id,
                    :message_id,
                    :edited_at,
                    :guild_id,
                    :content_before,
                    :content_after,
                    :user_id,
                    :jump_url)
            """,
            data
        )

        await self.bot.db.commit()

    async def _get_deleted_messages_member(self, member, amount):
        """Get the `amount` latest deleted emssages of a member."""

        async with self.bot.db.execute(
                """
                SELECT *
                FROM moderation_deletelog
                WHERE user_id = :user_id
                ORDER BY deleted_at DESC
                LIMIT :amount
                """,
                {
                    "amount": amount,
                    "user_id": member.id,
                }
        ) as c:
            rows = await c.fetchall()

        return rows

    async def _get_deleted_messages_channel(self, channel, amount):
        """Get the `amount` latest deleted emssages of a member."""

        async with self.bot.db.execute(
                """
                SELECT *
                FROM moderation_deletelog
                WHERE channel_id = :channel_id
                ORDER BY deleted_at DESC
                LIMIT :amount
                """,
                {
                    "amount": amount,
                    "channel_id": channel.id,
                }
        ) as c:
            rows = await c.fetchall()

        return rows
