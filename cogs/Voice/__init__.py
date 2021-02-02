from .voice import Voice


def setup(bot):
    bot.add_cog(Voice(bot))
