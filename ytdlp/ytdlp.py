import asyncio
import logging
import os
import subprocess
import tempfile

import discord

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.commands import Cog


logger = logging.getLogger("red")

from yt_dlp import YoutubeDL

class ytdlp(Cog):
    """
    Simple yt-dlp wrapper for Discord
    """

    def __init__(self, red: Red):
        super().__init__()
        self.bot = red

    @commands.command()
    async def ytdlp(self, ctx, url):
        """paste a url and get video uploaded to discord"""

        # this is terrible for now
        # 1. it's very easy for now to go over max attachment size on discord and we fail...
        # 2. it hangs whole bot when we do call to ydl.download
        # I wanted to do something better than just use subprocess and use library,
        # but looks like it won't work unless there's async support

        with tempfile.TemporaryDirectory() as dirname:
            ydl_opts = { 'outtmpl': f'{dirname}/%(title)s.%(ext)s', }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([ url ])

            filename = os.listdir(dirname)[0]

            await ctx.send(file=discord.File(dirname+'/'+filename))

