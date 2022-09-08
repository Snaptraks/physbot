from .wolframalpha import WolframAlpha


async def setup(bot):
    await bot.add_cog(WolframAlpha(bot))
