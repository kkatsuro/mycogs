from .uploadkey import uploadkey

async def setup(bot):
    await bot.add_cog(uploadkey(bot))
