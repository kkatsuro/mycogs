from .uploadssh import uploadssh

def setup(bot):
    bot.add_cog(uploadssh(bot))
