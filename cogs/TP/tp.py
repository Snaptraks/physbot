from discord.ext import commands


# COURS_TP_CATEGORY_ID = 804385332631175208  # test ID
COURS_TP_CATEGORY_ID = 801564568450236467


class TP(commands.Cog):
    """Module pour les fonctionnalités reliées aux cours / TP."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_voice_state_update")
    async def create_voice_channel(self, member, before, after):
        """Crée un nouveau VoiceChannel si ceux de la catégorie
        Cours/TP sont tous occupés.
        """
        category_before = self.get_category_channel_of_voice(before)
        category_after = self.get_category_channel_of_voice(after)

        category_after_id = getattr(category_after, "id", None)

        connected_to_category = (
            category_after_id == COURS_TP_CATEGORY_ID
            and category_before != category_after
        )

        if connected_to_category:
            # check number of empty channels
            empty = self.empty_voice_channels(category_after)

            if len(empty) == 0:
                # if no empty channel, create a new one
                last_channel_name = category_after.voice_channels[-1].name
                # assume a format "{PREFIX} {NUMBER}", ie "Voice 0"
                prefix, number = last_channel_name.split()
                new_channel_name = f"{prefix} {int(number) + 1}"
                await category_after.create_voice_channel(
                    new_channel_name,
                    reason="TP auto create",
                )

    @commands.Cog.listener(name="on_voice_state_update")
    async def delete_voice_channel(self, member, before, after):
        """Efface le VoiceChannel si il est vide, tout en laissant le
        channel 0.
        """
        category_before = self.get_category_channel_of_voice(before)
        category_before_id = getattr(category_before, "id", None)

        disconnected_from_channel = (
            category_before_id == COURS_TP_CATEGORY_ID
        )

        if disconnected_from_channel:
            # check number of empty channels
            empty = self.empty_voice_channels(category_before)

            if len(empty) > 1:
                # assume a format "{PREFIX} {NUMBER}", ie "Voice 0"
                prefix, number = before.channel.name.split()
                if number != "0":
                    to_delete = before.channel

                else:
                    # if everyone left from 0, delete the last empty one
                    to_delete = empty[-1]

                await to_delete.delete(reason="TP auto delete")

    def get_category_channel_of_voice(self, voice_state):
        """Return the category that the voice channel associated with the
        VoiceState is in. Return None if the VoiceState isn't connected
        to a channel, or the channel is not in a category.
        """
        try:
            channel = voice_state.channel

        except AttributeError:
            return None

        return getattr(channel, "category", None)

    def empty_voice_channels(self, category):
        """Return a list of empty VoiceChannels in the category."""

        return [vc for vc in category.voice_channels if not vc.members]
