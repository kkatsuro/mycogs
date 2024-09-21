from .remind import remind

async def setup(bot):
    await bot.add_cog(remind(bot))
