import re

import discord
from discord.ext import commands


class NotPrefixNumberFormatError(Exception):
    """Error raised when a voice channel does not have the
    <Prefix> <Number> format.
    """


class Voice(commands.Cog):
    """Module pour les fonctionnalités reliées aux salons vocaux."""

    def __init__(self, bot):
        self.bot = bot
        self.voice_channel_name_pattern = r"^(.+)\s(\d+)$"

    @commands.Cog.listener(name="on_voice_state_update")
    async def create_voice_channel(self, member, before, after):
        """Crée un nouveau VoiceChannel si ceux du format <Prefix> <Number>
        sont tous occupés.
        A besoin de la permission "Manage Channels".
        """
        if after.channel is not None:
            # if the member connects to a voice channel
            category_after = self.get_category_channel_of_voice(after)
            try:
                prefix, number = self.get_prefix_number(after.channel)
            except NotPrefixNumberFormatError:
                return

            # check number of empty channels
            prefixed_channels = self.get_matching_voice_channels(
                category_after, prefix)
            empty = self.empty_voice_channels(prefixed_channels)

            if len(empty) == 0:
                last_channel = prefixed_channels[-1]
                prefix, number = self.get_prefix_number(last_channel)
                new_channel_name = f"{prefix} {number + 1}"
                new_channel = await category_after.create_voice_channel(
                    new_channel_name,
                    reason="Channel auto create",
                    bitrate=member.guild.bitrate_limit,
                )
                await new_channel.edit(position=last_channel.position + 1)

    @commands.Cog.listener(name="on_voice_state_update")
    async def delete_voice_channel(self, member, before, after):
        """Efface le VoiceChannel si il est vide, tout en laissant le
        channel 1.
        A besoin de la permission "Manage Channels".
        """
        if before.channel is not None:
            # if the member was in a voice channel before
            category_before = self.get_category_channel_of_voice(before)
            try:
                prefix, number = self.get_prefix_number(before.channel)
            except NotPrefixNumberFormatError:
                return

            # check number of empty channels
            prefixed_channels = self.get_matching_voice_channels(
                category_before, prefix)
            empty = self.empty_voice_channels(prefixed_channels)
            vc_names = '\n'.join([vc.name for vc in empty])

            if len(empty) > 1:
                to_delete = empty[-1]  # delete the last empty channel
                prefix, number = self.get_prefix_number(to_delete)

                if number == 1:
                    print(
                        "TRIED TO DELETE CHANNEL 1\n"
                        f"{vc_names}"
                    )
                    return

                try:
                    await to_delete.delete(reason="Channel auto delete")

                except discord.NotFound:
                    # channel already deleted, probably
                    pass

    def get_prefix_number(self, channel):
        """Get the prefix and number of a channel's name, if it is in
        the format <Prefix> <Number>, otherwise raise SomeError.
        """

        match = re.fullmatch(self.voice_channel_name_pattern, channel.name)
        if match:
            prefix, number = match.group(1, 2)
            number = int(number)
            return prefix, number

        else:
            raise NotPrefixNumberFormatError(
                f"{channel.name} does not have the right format.")

    def get_matching_voice_channels(self, category, prefix):
        """Return a list of the voice channels with the matching prefix
        in the category.
        """
        return [vc for vc in category.voice_channels
                if re.fullmatch(rf"^{prefix}\s\d+$", vc.name)]

    def get_category_channel_of_voice(self, voice_state):
        """Return the category that the voice channel associated with the
        VoiceState is in. Return the Guild if the VoiceStateis not in a
        category or None if it isn't connected.
        """
        try:
            channel = voice_state.channel

        except AttributeError:
            return None

        return channel.category or channel.guild

    def empty_voice_channels(self, channels):
        """Return a list of empty VoiceChannels in the list channels."""

        return [vc for vc in channels if not vc.members]
