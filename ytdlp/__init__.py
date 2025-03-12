from .ytdlp import ytdlp

async def setup(bot):
    await bot.add_cog(ytdlp(bot))
