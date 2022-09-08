from .voice import Voice


async def setup(bot):
    await bot.add_cog(Voice(bot))
