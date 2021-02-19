import discord
from discord.ext import menus
from discord.ext.menus import MenuPages


class DeletedMessagesMenu(MenuPages):
    async def send_initial_message(self, ctx, channel):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await ctx.reply(**kwargs)


class DeletedMessagesSource(menus.ListPageSource):
    def __init__(self, entries):
        super().__init__(entries, per_page=1)

    async def format_page(self, menu, entries):
        content = entries['content']
        user_id = entries["user_id"]
        if user_id is not None:
            author = (menu.bot.get_user(user_id)
                      or await menu.bot.fetch_user(user_id))
        else:
            author = "[Author not in cache or unavailable]"

        if content is None:
            content = "[Content not in cache or unavailable]"

        embed = discord.Embed(
            title=(
                f"{len(self.entries)} latest deleted messages for "
                f"{menu.ctx.invoked_with.title()} {menu.ctx.args[2]}"
            ),
            description=f"```\n{content}\n```",
            color=discord.Color.red(),
        ).set_author(
            name="Deleted Messages Log",
        ).set_footer(
            text=f"Page {menu.current_page + 1} / {self.get_max_pages()}",
        ).add_field(
            name="Author",
            value=author,
        )
        for key in entries.keys():
            if key == "content":
                continue
            embed.add_field(
                name=key,
                value=entries[key],
            )

        return embed
