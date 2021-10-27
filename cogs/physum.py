import discord
from discord.ext import commands


class Physum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = discord.utils.get(guild.channels, name="rôles")
        if guild.system_channel is not None:
            to_send = (
                f"Bienvenue {member.mention} dans le serveur de la Physum!\n"
                f"Choisis ton année et ton programme dans {channel.mention} "
                "pour avoir accès à plus de salons et de fun :) "
            )
            await guild.system_channel.send(to_send)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Give the PHYSUM role to members selecting a "year" role.
        Temporary thing until we have the whole role selection module.
        """

        program_role_ids = [
            750170200674140190,  # physique
            750146644229619785,  # phys-info
            750146609542725703,  # maths-phys
        ]
        physum_role_id = 775463611106983957  # physum
        physum_role = after.guild.get_role(physum_role_id)

        before_role_ids = [role.id for role in before.roles]
        after_role_ids = [role.id for role in after.roles]

        before_has_program = any([id in program_role_ids for id in before_role_ids])
        after_has_program = any([id in program_role_ids for id in after_role_ids])

        if before_role_ids != after_role_ids:
            # if the roles changed
            try:
                if not before_has_program and after_has_program:
                    # if the member now has a year role
                    await after.add_roles(physum_role)

                elif before_has_program and not after_has_program:
                    # if the member now _has not_ a year role:
                    await after.remove_roles(physum_role)

                else:
                    # some other roles were added
                    pass

            except (discord.Forbidden, discord.HTTPException):
                # raise if we can't add roles
                raise


def setup(bot):
    bot.add_cog(Physum(bot))
