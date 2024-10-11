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
from datetime import datetime

logger = logging.getLogger("red")


# directory structure is (will be.. after I do link creation, @todo):
# backup-dir/
# | - guild1-id/
# |   | - channel-id1/
# |   |   | - messages.log
# |   |   | - attachments/
# |   |
# |   | - channel-id2/
# |       | - messages.log
# |       | - attachments/
# |
# | - guild1-name/
#     | - link-to-channel-id1-with-name
#     | - link-to-channel-id2-with-name


class backup(Cog):
    """
    backup everything!!
    """

    def __init__(self, red: Red):
        super().__init__()
        self.bot = red

        self.config = Config.get_conf(self, identifier=5134513541)
        self.config.register_global(disabled_channels=[])

        self.backup_directory = f'{os.environ["HOME"]}/.local/share/F4P-Backup'
        self.watched_channels = set()
        self.backup_tasks = {}

    async def cog_load(self):
        disabled_channels = await self.config.disabled_channels()
        async for guild in self.bot.fetch_guilds():
            for channel in await guild.fetch_channels():
                if channel in disabled_channels:
                    continue
                self.backup_tasks[channel.id] = asyncio.create_task(self.perform_backup(channel))

        logger.info('== loaded backup ==')

    async def cog_unload(self):
        for task in self.backup_tasks.values():
            task.cancel()

    @commands.group()
    async def backup(self, ctx):
        pass

    # @todo: add way to specify channel id or discord channel
    @backup.command()
    async def disable(self, ctx):
        '''
        Disable channel from backup
        '''
        async with self.config.disabled_channels() as channels:
            if ctx.channel.id in channels:
                return await ctx.send('Channel was already disabled')
            channels.append(ctx.channel.id)

        # asyncio.create_task(self.perform_backup(ctx.channel))
        # @todo: get backup task and backup_dict thingie, and disable it from there

        await ctx.send('Disabled from backup')

    @backup.command()
    async def enable(self, ctx):
        '''
        Enable backup for current channel again
        '''
        async with self.config.disabled_channels() as channels:
            if ctx.channel.id not in channels:
                return await ctx.send('Channel was not disabled')
            channels = [ id for id in channels if id != ctx.channel.id ]
            # @todo: stop task too, both perform_backup and self.watched_channels.dicard(id)
        await ctx.send('Backup enabled again')

    @commands.command()
    async def embed_details(self, ctx, message_id=None):
        if message_id is None:
            message_id = 1292423726905823264
        message = await ctx.channel.fetch_message(message_id)
        await ctx.send(str(message.embeds[0].to_dict()))
        # await ctx.send(str(message.content))


    async def save_message(self, message):
        channel_directory = f'{self.backup_directory}/{message.guild.id}/{message.channel.id}'

        message_dict = {
            'id': message.id,
            'author': message.author.id,
            'date': str(message.created_at)
        }

        if message.embeds:
            embeds = [ embed.to_dict() for embed in message.embeds ]
            message_dict['embeds'] = embeds

        if message.content:
            message_dict['content'] = message.content

        if message.attachments:
            message_dict['attachments'] = []
            for file in message.attachments:
                filename = f'{message.id}-{file.filename}'
                asyncio.create_task(file.save(f'{channel_directory}/attachments/{filename}'))
                message_dict['attachments'].append(filename)

        if message.reference:
            message_dict['reference'] = message.reference.message_id

        logfile = f'{channel_directory}/messages.log'
        with open(logfile, 'a') as f:
            f.write(f'{message.created_at.timestamp()} {json.dumps(message_dict)}\n')


    async def perform_backup(self, channel):
        '''
        Starts saving of channel history to the channel logfile
        Looks at the last message in logfile, then starts checking history after it
        Wrong channel can be provided, it will just return
        Looks like permissions are not really reliable,
        so I try to download one message to see if bot actually has permission
        '''
        if not isinstance(channel, discord.TextChannel):
            return

        try:
            async for message in channel.history(limit=1, oldest_first=True):
                pass
        except discord.Forbidden:
            return

        logger.info(f'Starting perform_backup({channel.name})')

        try:
            channel_dir = f'{self.backup_directory}/{channel.guild.id}/{channel.id}'
            messages_file = f'{channel_dir}/messages.log'

            # load date of last message
            if os.path.isfile(messages_file):
                with open(messages_file) as f:
                    # seek near the end of file.. some files will be veeeery big, dont wonna load those
                    # I sent a message full of 4bytes unicode character and clength of the line was 12132 characters,
                    # so I will do 64k here for no good reason other than it's few times bigger
                    f.seek(0, 2)
                    file_size = f.tell()
                    limit = 2**16
                    if file_size > limit:
                        f.seek(file_size-limit)

                    try:
                        lastline = None  # makes debug message bellow always work
                        lastline = f.read().splitlines()[-1]
                        timestamp, _ = lastline.split(maxsplit=1)
                        last_message_date = datetime.fromtimestamp(float(timestamp))
                    except Exception as e:
                        logger.info(f'Error while parsing date from last message: {e}; lastline is: {lastline}')
                        last_message_date = None
            else:
                last_message_date = None

            attachments_dir = f'{channel_dir}/attachments'
            if not os.path.isdir(attachments_dir):
                os.makedirs(attachments_dir)

            # it gets saved here, so we can later use some script which will create links to channels
            # with channel names, instead of ids
            with open(f'{channel_dir}/channel_name.log', 'w') as f:
                f.write(channel.name)

            async for message in channel.history(limit=None, oldest_first=True, after=last_message_date):
                await self.save_message(message)

            self.watched_channels.add(channel.id)

        except Exception as e:
            logger.info(f'Error in perform_backup({channel.name}): {e}')


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id not in self.watched_channels:
            return
        await self.save_message(message)
