import asyncio
import logging
import os
import subprocess

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

    @commands.command()
    async def showip(self, ctx):
        """show login address of server"""
        process = subprocess.run(['curl', 'ipconfig.io'], stdout=subprocess.PIPE)
        await ctx.send(f'`{os.getenv("USER")}@{process.stdout}`')
