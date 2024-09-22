import asyncio
import logging
import random
import json
import os
import shutil

import discord
from discord.ext import tasks
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.commands import Cog
from redbot.core.utils.predicates import MessagePredicate

from tempfile import TemporaryFile

logger = logging.getLogger("red")

class exportserver(Cog):
    """
    about cog
    """

    def __init__(self, red: Red):
        super().__init__()
        self.bot = red

        if self.bot.is_ready():
            asyncio.create_task(self.load())


    async def load(self):
        logger.info('== loaded exportserver ==')


    async def savechannel(self, channel, root_directory, limit=None):
        directory = f'{root_directory}/{channel.id}'
        attachments_directory = f'{directory}/attachments'
        os.mkdir(directory)
        os.mkdir(attachments_directory)
        # we save attachments to attachments_directory
        # and messages to dirname/messages.json

        i = 1

        messages = []
        async for message in channel.history(limit=limit):
            if i % 937 == 0:  # some random number for logs
                logger.info(f'{channel.id} -- message {i}')
            i += 1

            # @todo: improve this one
            message_dict = {
                'id': message.id,
                'author': message.author.id,
                'date': str(message.created_at)
            }

            if message.content:
                message_dict['content'] = message.content

            if message.attachments:
                message_dict['attachments'] = [ file.filename for file in message.attachments ]
                for file in message.attachments:
                    asyncio.create_task(file.save(f'{attachments_directory}/{message.id}-{file.filename}'))

            if message.reference:
                message_dict['reference'] = message.reference.message_id

            messages.insert(0, message_dict)

        filename = f'{directory}/messages.json'
        with open(filename, 'w') as f:
            f.write(json.dumps(messages, indent=2))


    @commands.command()
    async def saveguild(self, ctx, limit=None):
        dirname = f'/tmp/guild-{ctx.guild.id}'
        await ctx.send(f'saving guild!')
        try:
            shutil.rmtree(dirname)
        except:
            pass
        os.mkdir(dirname)
        # await ctx.send(f'channels: {ctx.guild.channels}')
        # 
        for channel in await ctx.guild.fetch_channels():
            if not isinstance(channel, discord.TextChannel):
                continue

            perms = channel.permissions_for(ctx.me)
            if not (perms.read_messages and perms.read_message_history):
                continue

            try:
                await self.savechannel(channel, dirname, limit)
                await ctx.send(f'saved channel {channel.name} -- {channel.id}')
            except Exception as e:
                await ctx.send(f'error saving channel {channel.name}: {e}')

        # this gives wrong size actually..
        await ctx.send(f'saving guild done!! guild size is: {round(shutil.disk_usage(dirname).used/1024/1024, 2)} MB')

