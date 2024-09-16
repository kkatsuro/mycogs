from .fap import fap

async def setup(bot):
    await bot.add_cog(fap(bot))
