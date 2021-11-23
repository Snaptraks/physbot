import discord
from discord import ButtonStyle
from discord.ui import View, Button, Select


class RolesSelect(Select):
    def __init__(self, roles, toggle=False):
        options = [discord.SelectOption(label=role.name) for role in roles]
        self.id_map = {role.name: role.id for role in roles}
        super().__init__(
            placeholder="Select roles",
            options=options,
            max_values=1 if toggle else len(options),
            custom_id="rolesview:select",
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        selected_roles = [guild.get_role(self.id_map[name]) for name in self.values]
        self.view.selected_roles[interaction.user] = selected_roles


class RolesView(View):
    def __init__(self, roles: list[discord.Role]):
        select = RolesSelect(roles)
        super().__init__(timeout=None)
        self.add_item(select)
        self.selected_roles = {}

    @discord.ui.button(
        label="Add",
        style=ButtonStyle.green,
        emoji="\N{HEAVY PLUS SIGN}",
        custom_id="rolesview:add",
        row=4,
    )
    async def add_roles(self, button: Button, interaction: discord.Interaction):
        member = interaction.user
        await member.add_roles(*self.selected_roles[member])
        await interaction.response.send_message(
            f"Adding roles {self.selected_roles[member]} to {repr(member)}",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Remove",
        style=ButtonStyle.red,
        emoji="\N{HEAVY MINUS SIGN}",
        custom_id="rolesview:remove",
        row=4,
    )
    async def remove_roles(self, button: Button, interaction: discord.Interaction):
        member = interaction.user
        await member.remove_roles(*self.selected_roles[member])
        await interaction.response.send_message(
            f"Removing roles {self.selected_roles[member]} to {repr(member)}",
            ephemeral=True,
        )
