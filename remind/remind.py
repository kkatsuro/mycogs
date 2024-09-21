import asyncio
import logging
import random
import time
import humanize

from datetime import datetime, timedelta

import discord
from discord.ext import tasks
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.commands import Cog
from redbot.core.utils.predicates import MessagePredicate

logger = logging.getLogger("red")

DISGUST = '<:kurumDisgust:973260944593530991>'


def date_split_one(date):
    '''
    for date - '31d5h43s' - returns '31', 'd', '5h43s'
    for '43s' returns '43', 's', ''
    '''
    for i, char in enumerate(date):
        if not char.isdigit():
            number = date[:i]
            date = date[i+1:]
            return number, char, date

    return '', '', ''


class remind(Cog):
    """
    aaaaaaaaaaaaaaaaaaaaaaa
    """

    def __init__(self, red: Red):
        super().__init__()
        self.bot = red

        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_global(saved_dates={})

        self.reminder_tasks = []

    async def cog_load(self):
        reminders = await self.config.saved_dates()
        for reminder in reminders.values():
            asyncio.create_task(self.send_reminder_from_conf(reminder))

        logger.info('== loaded remind ==')

    async def cog_unload(self):
        for task in self.reminder_tasks:
            task.cancel()

    async def send_reminder_from_conf(self, reminder):
        channel = await self.bot.fetch_channel(reminder['channel'])
        user = await self.bot.fetch_user(reminder['user'])
        self.reminder_tasks.append(
            asyncio.create_task(self.send_reminder(channel, user, reminder['thing'], reminder['when']))
        )

    async def send_reminder(self, channel, user, thing, timestamp):
        await asyncio.sleep(timestamp - time.time())
        await channel.send(f'Hey, {user.mention}!')
        await channel.send(f'Remember to {thing}, you bastard {DISGUST}')

        async with self.config.saved_dates() as dates:
            del dates[str(timestamp)]

    @commands.command()
    async def remind(self, ctx, when, *, thing):
        """
        Reminds about something in the future

        just use a number with **one** letter, it's quite simple
        w - weeks, d - days, h - hours, m - minutes, s - seconds

        months unsupported, we don't have such fancy features, sorry <:Sadge:932030197891469312>
        but wait.. u can use 30 days instead of 1 month! <:poggers:973260944727769098>
        thats sick, right?

        usage:
          &remind 30m Apple pie is done!!
          &remind 2w3d4h5m6s 1week and some time passed..
        """

        letters = { 'w': 'weeks', 'd': 'days', 'h': 'hours', 'm': 'minutes', 's': 'seconds' }
        timeframe = {}

        while when:
            number, letter, when = date_split_one(when)
            if number == '':
                return await ctx.send('You should specify number for your date, check &help remind')
            
            if (full_name := letters.get(letter)) is None:
                return await ctx.send(f'Unrecognized date letter: `{letter}`')

            timeframe[full_name] = int(number)

        delta = timedelta(**timeframe)
        date = datetime.now() + timedelta(**timeframe)
        timestamp = date.timestamp()

        reminder = {
            'user': ctx.author.id,
            'when': timestamp,
            'thing': thing,
            'channel': ctx.channel.id
        }

        # save to config 
        async with self.config.saved_dates() as dates:
            dates[str(timestamp)] = reminder

        self.reminder_tasks.append(
            asyncio.create_task(self.send_reminder(ctx.channel, ctx.author, thing, timestamp))
        )

        duration = humanize.naturaldelta(delta).replace(' ', '-')
        if duration.startswith('a-'):
            duration.replace('a', '1', 1)
        await ctx.send(f'Initiating a {duration} time leap. See ya soon, you bastards. {DISGUST}')
