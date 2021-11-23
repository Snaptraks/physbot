from secrets import token_hex

import discord
from discord import ButtonStyle
from discord.ui import View, Button, Select, Item


class RolesSelect(Select):
    def __init__(self, roles, custom_id, toggle=False):
        options = [discord.SelectOption(label=role.name) for role in roles]
        self.id_map = {role.name: role.id for role in roles}
        super().__init__(
            placeholder="Select roles",
            options=options,
            max_values=1 if toggle else len(options),
            custom_id=custom_id,
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        selected_roles = [guild.get_role(self.id_map[name]) for name in self.values]
        self.view.selected_roles[interaction.user] = selected_roles


class RolesView(View):
    def __init__(self, roles: list[discord.Role], components_id: dict[str, str] = None):
        super().__init__(timeout=None)

        if components_id is None:
            components_id = {
                "select_id": token_hex(16),
                "add_id": token_hex(16),
                "remove_id": token_hex(16),
            }
        self.components_id = components_id

        select = RolesSelect(roles, components_id["select_id"])
        self.add_item(select)
        self.selected_roles = {}

        add = Button(
            label="Add",
            style=ButtonStyle.green,
            emoji="\N{HEAVY PLUS SIGN}",
            custom_id=components_id["add_id"],
            row=4,
        )
        add.callback = self.button_callback("add_roles")
        self.add_item(add)

        remove = Button(
            label="Remove",
            style=ButtonStyle.red,
            emoji="\N{HEAVY MINUS SIGN}",
            custom_id=components_id["remove_id"],
            row=4,
        )
        remove.callback = self.button_callback("remove_roles")
        self.add_item(remove)

    def button_callback(self, method: str):
        async def callback(interaction: discord.Interaction):
            member = interaction.user
            add_remove_roles = getattr(member, method)
            await add_remove_roles(*self.selected_roles[member])
            roles_str = ", ".join(role.mention for role in self.selected_roles[member])
            await interaction.response.send_message(
                f"Changing roles {roles_str} for member {member.mention}",
                ephemeral=True,
            )

        return callback

    async def on_error(
        self, error: Exception, item: Item, interaction: discord.Interaction
    ):
        if isinstance(error, KeyError):
            await interaction.response.send_message(
                "There was an error. You need to select at least one role.",
                ephemeral=True,
            )
        else:
            raise error
