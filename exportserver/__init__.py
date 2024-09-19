from .exportserver import exportserver

async def setup(bot):
    await bot.add_cog(exportserver(bot))
