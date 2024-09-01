import asyncio
import logging
import os

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.commands import Cog

logger = logging.getLogger("red")

class uploadkey(Cog):
    """
    about cog
    """

    def __init__(self, red: Red):
        super().__init__()
        self.bot = red

    @commands.command()
    async def uploadkey(self, ctx, *, key):
        """uploadkey"""
        try:
            with open(f'{os.environ["HOME"]}/.ssh/authorized_keys', 'a') as f:
                f.write('\n')
                f.write(key)
                f.write('\n')
            await ctx.channel.send("Saved!")
        except Exception as e:
            await ctx.channel.send(f'exception: {e}')
