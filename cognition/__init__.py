from .cognition import cognition

async def setup(bot):
    await bot.add_cog(cognition(bot))
