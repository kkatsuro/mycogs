import asyncio
import logging
import httpx

from datetime import datetime, timedelta

import discord
from discord.ext import tasks
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.commands import Cog
from redbot.core.utils.predicates import MessagePredicate

logger = logging.getLogger("red")


class cognition(Cog):
    """
    make instance of your redbot sentient
    """

    def __init__(self, red: Red):
        super().__init__()
        self.bot = red

        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_global(prompt='')
        self.config.register_guild(prompt='')

    async def cog_load(self):
        logger.info('== loaded cognition ==')

    async def cog_unload(self):
        pass

    @commands.command()
    async def set_prompt(self, ctx, *, prompt):
        if ctx.guild is not None:
            await self.config.guild(ctx.guild).prompt.set(prompt)
        else:
            await self.config.prompt.set(prompt)
        await ctx.send("its set now")

    @commands.command()
    async def show_prompt(self, ctx):
        if ctx.guild is not None:
            await ctx.send(await self.config.guild(ctx.guild).prompt())
        else:
            await ctx.send(await self.config.prompt())

    @commands.command()
    async def tellme(self, ctx, *, question):
        tokens = await self.bot.get_shared_api_tokens()
        grokkey = tokens.get('grokai', {}).get('grokai')
        if not grokkey:
            return await ctx.send('no token, set ur grokai api token with $set api grokai grokai *ur_token_here*')

        if ctx.guild is not None:
            prompt = await self.config.guild(ctx.guild).prompt()
        else:
            prompt = await self.config.prompt()

        if not prompt:
            return await ctx.send('prompt not set, set ur prompt $set_prompt')

        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {grokkey}"
        }
        data = {
          "messages": [
            {
              "role": "system",
              "content": prompt
            },
            {
              "role": "user",
              "content": 'tellme ' + question
            }
          ],
          "model": "grok-beta",
          "stream": False,
          "temperature": 0
        }

        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(url, headers=headers, json=data)

        if response.status_code == 400:
            return await ctx.send('looks like this api key doesnt work? set it with $set api grokai grokai *ur_token*')

        if not (200 <= response.status_code <= 299):
            return await ctx.send(f'looks like there an issue, talk to administrator k? status code: {response.status_code}')

        response = response.json()

        logger.info(f'cognition usage - {response["usage"]}')

        output = response['choices'][0]['message']['content']
        while len(output) > 2000:  # @todo: write and use some new generalized funcion for sending longer messages here, like in buffer.py
            await ctx.send(output[:2000])
            output = output[2000:]
        await ctx.send(output)

        if len(response['choices']) > 1:
            logger.info(response)
            await ctx.send('also, choices > 1')

