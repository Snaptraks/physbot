from collections import defaultdict
from datetime import datetime
import re
from typing import Union

import discord
from discord.ext import commands, tasks
from discord.utils import parse_time

from . import menus

ADMIN_CHANNEL = 750166269860249671


def find_not_None(sequence, key):
    """Helper method to find the first entry that is not None in the
    sequence with the given key.
    """
    return discord.utils.find(lambda x: x[key] is not None, sequence)[key]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self._create_tables.start()

    def cog_check(self, ctx):
        return commands.has_guild_permissions(administrator=True,).predicate(ctx)

    @commands.Cog.listener(name="on_message")
    async def delete_fake_nitro_scam(self, message):
        url_pattern = (
            r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))"
            r"([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
        )
        has_url = re.search(url_pattern, message.content)
        nitro_message = "Discord is giving away nitro!"

        if nitro_message in message.content and has_url:
            admin_channel = self.bot.get_channel(ADMIN_CHANNEL) or message.channel
            scam_author = message.author

            try:
                await message.delete()

            except discord.Forbidden:
                is_deleted = "Could not delete"

            else:
                is_deleted = "Deleted"

            try:
                await scam_author.ban(reason="Nitro Scam")

            except discord.Forbidden:
                is_banned = "could not ban"

            else:
                is_banned = "banned"

            await admin_channel.send(
                f"{is_deleted} a potential scam message in {message.channel.mention} "
                f"and {is_banned} user {scam_author} ({scam_author.id})"
            )

    @commands.Cog.listener(name="on_raw_message_delete")
    async def log_deleted_message(self, payload):
        """Save when a message is deleted, in the database.
        Try to save as much information as possible.
        """
        if not payload.guild_id:
            # ignore DM messages
            return

        data = defaultdict(lambda: None)
        data.update(
            {
                "channel_id": payload.channel_id,
                "guild_id": payload.guild_id,
                "message_id": payload.message_id,
                "deleted_at": datetime.utcnow(),
            }
        )

        cached_message = payload.cached_message  # can be None
        if cached_message:
            data.update(
                {
                    "content": cached_message.clean_content,
                    "user_id": cached_message.author.id,
                    "jump_url": cached_message.jump_url,
                }
            )

        await self._log_deleted_message(data)

    @commands.Cog.listener(name="on_raw_message_edit")
    async def log_edited_message(self, payload):
        """Save when a message is edited, in the database.
        Try to save as much information as possible.
        """
        if not payload.data.get("content"):
            # not a content edit
            return

        data = defaultdict(lambda: None)
        data.update(
            {
                "channel_id": payload.channel_id,
                "message_id": payload.message_id,
                "edited_at": parse_time(payload.data.get("edited_timestamp")),
                "content_after": payload.data["content"],  # will always be present
                "guild_id": payload.data.get("guild_id"),
            }
        )

        message = payload.cached_message  # can be None
        if message is None:
            channel = self.bot.get_channel(payload.channel_id)
            # should always be found
            message = await channel.fetch_message(payload.message_id)
            content_before = None

        else:
            content_before = message.content

        if message:
            data.update(
                {
                    "content_before": content_before,
                    "user_id": message.author.id,
                    "jump_url": message.jump_url,
                }
            )

        await self._log_edited_message(data)

    @commands.command(aliases=["user", "user_info", "member"])
    async def member_info(self, ctx, *, member: discord.Member = None):
        """Return info about a member."""

        if member is None:
            member = ctx.author

        embed = (
            discord.Embed(title=str(member), color=discord.Color.blurple(),)
            .add_field(
                name="User information",
                value=(
                    f"Created: {member.created_at}\n"
                    f"Profile: {member.mention}\n"
                    f"ID: {member.id}"
                ),
                inline=False,
            )
            .add_field(
                name="Member information",
                value=(f"Joined: {member.joined_at}\n" f"{len(member.roles)} roles"),
                inline=False,
            )
            .set_thumbnail(url=member.avatar_url_as(format="png"),)
        )

        await ctx.reply(embed=embed)

    @commands.group(invoke_without_command=True)
    async def deletelog(
        self,
        ctx,
        msg_source: Union[discord.Member, discord.TextChannel],
        amount: int = 10,
    ):
        """Command group to see deleted messages of a member or a channel."""

        if isinstance(msg_source, discord.Member):
            deleted_messages = await self._get_deleted_messages_member(
                msg_source, amount
            )

        elif isinstance(msg_source, discord.TextChannel):
            deleted_messages = await self._get_deleted_messages_channel(
                msg_source, amount
            )

        menu = menus.DeletedMessagesMenu(
            source=menus.DeletedMessagesSource(deleted_messages),
            clear_reactions_after=True,
        )
        await menu.start(ctx)

    @deletelog.error
    async def deletelog_error(self, ctx, error):
        """Error handler for the deletelog subcommands."""

        if isinstance(error, commands.BadUnionArgument):
            await ctx.reply(error)

        else:
            raise error

    @commands.command()
    async def editlog(
        self, ctx, message: Union[discord.Message, discord.PartialMessage]
    ):
        """Get the revisions of a message."""

        message_id, channel_id = message.id, message.channel.id
        edited_messages = await self._get_edited_messages(message_id, channel_id)

        if len(edited_messages) == 0:
            await ctx.reply("No edits of this message recorded")
            return

        if isinstance(message, discord.Message):
            author = message.author
            channel = message.channel
            jump_url = message.jump_url
            deleted = False

        elif isinstance(message, discord.PartialMessage):
            author = self.bot.get_user(find_not_None(edited_messages, "user_id"))
            channel = message.channel
            jump_url = find_not_None(edited_messages, "jump_url")
            deleted = True

        description = f"Message sent by {author} in {channel.mention}.\n"
        if jump_url:
            description += f"[Jump to message]({jump_url})"
            if deleted:
                description += " (now deleted)"

        embed = (
            discord.Embed(
                title="Message Revisions",
                description=description,
                color=discord.Color.red(),
            )
            .set_author(name=author,)
            .add_field(
                name="Original",
                value=f"```\n{edited_messages[0]['content_before']}\n```",
                inline=False,
            )
            .add_field(
                name="Revision 1",
                value=f"```\n{edited_messages[0]['content_after']}\n```",
                inline=False,
            )
        )

        for i, edited in enumerate(edited_messages[1:]):
            embed.add_field(
                name=f"Revision {i + 2}",
                value=f"```\n{edited['content_after']}\n```",
                inline=False,
            )

        await ctx.reply(embed=embed)

    @editlog.error
    async def editlog_error(self, ctx, error):
        """Error handler for the editlog command."""

        error = getattr(error, "original", error)
        if isinstance(error, discord.HTTPException):
            # TODO: have way of checking too-big-to-print edits
            await ctx.reply("Command output likely too big.")

        elif isinstance(
            error, (commands.BadArgument, commands.MissingRequiredArgument)
        ):
            await ctx.reply(error)

        else:
            raise error

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
            data,
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
            data,
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
            {"amount": amount, "user_id": member.id},
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
            {"amount": amount, "channel_id": channel.id},
        ) as c:
            rows = await c.fetchall()

        return rows

    async def _get_edited_messages(self, message_id, channel_id):
        """Get the revisions of a message."""

        async with self.bot.db.execute(
            """
            SELECT *
              FROM moderation_editlog
             WHERE message_id = :message_id
               AND channel_id = :channel_id
             ORDER BY edited_at
            """,
            {"message_id": message_id, "channel_id": channel_id},
        ) as c:
            rows = await c.fetchall()

        return rows
