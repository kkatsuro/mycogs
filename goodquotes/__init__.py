from .goodquotes import goodquotes

async def setup(bot):
    await bot.add_cog(goodquotes(bot))
