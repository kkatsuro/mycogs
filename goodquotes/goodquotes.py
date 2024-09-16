import asyncio
import logging
import httpx
import random

from bs4 import BeautifulSoup

import discord
from discord.ext import tasks
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.commands import Cog
from redbot.core.utils.predicates import MessagePredicate

logger = logging.getLogger("red")

def parse_quote(quote_soup):
    quote = dict()

    # @todo: some logging on every except?
    try:
        text = quote_soup.find(class_='quoteText')
        quote['text'] = str(text).splitlines()[1].strip().replace('<br>', '\n')
    except:
        quote['text'] = None

    try:
        quote['picture'] = quote_soup.find(class_='leftAlignedImage').img['src']
    except:
        quote['picture'] = None

    try:
        quote['author'] = str(quote_soup.find(class_='authorOrTitle')).splitlines()[1]
    except:
        quote['author'] = None

    try:
        tags = quote_soup.find(class_='quoteFooter')
        quote['tags'] = [ tag.string for tag in tags.find_all('a')[:-1] ]
    except:
        quote['tags'] = None

    try:
        quote['link'] = quote_soup.find(class_='right').find('a')['href']
    except:
        quote['link'] = None

    return quote


async def get_random_quote():
    async with httpx.AsyncClient() as client:
        r = await client.get('https://www.goodreads.com/quotes', params={'page': random.randint(1, 100)})

    if r.status_code != 200:  # @todo: handle this somehow!!
        logger.error(f'goodreads quotes status != 200; status: {r.status_code}; r: {r}')
        return None
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        quote = random.choice(soup.find_all('div', class_='quote'))
        quote = parse_quote(quote)

        embed = discord.Embed(description=f"*{quote['text']}* -- {quote['author']}")
        if quote['picture']:
            embed.set_thumbnail(url=quote['picture'])
        return embed

    except Exception as e:
        logger.error(e)
        return None

def create_buggy_quote_embed():
    text = 'If debugging is the process of removing software bugs, '  \
           'then programming must be the process of putting them in.'
    author = 'Edsger W. Dijkstra '
    embed = discord.Embed(description=f'*{text}* -- {author}\n\n(yes, I fucked up)')
    embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Edsger_Wybe_Dijkstra.jpg/330px-Edsger_Wybe_Dijkstra.jpg')
    return embed

class goodquotes(Cog):
    """
    quotes from goodreads
    """

    def __init__(self, red: Red):
        super().__init__()
        self.bot = red
        if self.bot.is_ready():
            asyncio.create_task(self.load())

    async def load(self):
        logger.info('== loaded goodquotes ==')

    @commands.command()
    async def quote(self, ctx):
        """goodread quote!!"""
        quote_embed = await get_random_quote()
        if quote_embed == None:
            quote_embed = create_buggy_quote_embed()
        await ctx.channel.send(embed=quote_embed)
