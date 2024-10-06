from .backup import backup

async def setup(bot):
    await bot.add_cog(backup(bot))
