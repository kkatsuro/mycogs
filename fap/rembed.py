import discord

async def fetch_message_from_reference(ref, ctx):
    channel = ctx.guild.get_channel(ref.channel_id)
    if channel == None:  # can this even happen?
        raise Exception('could not find such channel')

    return await channel.fetch_message(ref.message_id)


async def create_reply_embed_from_ref(channel, ref, author_in_title=True):
    msg = ref.cached_message
    if msg == None:
        msg = await channel.fetch_message(ref.message_id)

    if msg == None:
        await channel.send('Message deleted or something')
        return None

    link =  'https://discord.com/channels/'\
           f'{ref.guild_id}/{ref.channel_id}/{ref.message_id}'

    return create_reply_embed(msg, link, author_in_title)


# XXX: how we use this?
def create_reply_embed(msg, link, author_in_title=True):
    color = msg.author.color
    timestamp = msg.edited_at if msg.edited_at else msg.created_at

    if author_in_title:
        text  = '' + msg.content
        embed = discord.Embed(color=color, description=text,
                              timestamp=timestamp, title=msg.author.display_name,
                              url=link, type='rich')
    else:
        text = f'{msg.content} \n\n [see msg]({link})'
        embed = discord.Embed(color=color, description=text,
                              timestamp=timestamp,
                              url=link, type='rich')

    if not author_in_title:
        embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)
    else:
        embed.set_thumbnail(url=msg.author.avatar_url)

    if len(msg.attachments) > 0:
        embed.set_image(url=msg.attachments[0].url)

    return embed


# should we have these member checks here?
# you can't use it for other purposes (like cat_cache message existance check)
async def fetch_message_from_link(ctx, link):
    link_split = link.split('/')
    if len(link_split) != 7:
        await ctx.channel.send('This doesn\'t look like a valid link')
        return None

    link_split = link_split[-3:]
    for link_id in link_split:
        if not link_id.isnumeric():
            await ctx.channel.send('This doesn\'t look like a valid link')
            return None

    guild_id, channel_id, message_id = [ int(link_id) for link_id in link_split ]

    guild = ctx.bot.get_guild(guild_id)
    if guild == None:
        await ctx.channel.send('I don\'t have access to this guild')
        return None

    if guild.get_member(ctx.author.id) == None:
        await ctx.channel.send('You\'re not member of this guild')
        return None

    channel = guild.get_channel(channel_id)
    if channel == None:
        await ctx.channel.send('Channel doesn\'t exist in this guild')
        return None

    if ctx.author not in channel.members:
        await ctx.channel.send('You don\t have access to this channel')
        return None

    msg = await channel.fetch_message(message_id)
    if msg == None:
        await ctx.channel.send('Couldn\'t find message')
        return None

    return msg
