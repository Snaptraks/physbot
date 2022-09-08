from .tex import TeX


async def setup(bot):
    await bot.add_cog(TeX(bot))
