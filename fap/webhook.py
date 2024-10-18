import asyncio
import discord
import logging

from discord.errors import NotFound

# @todo: its possible a lock is necessary on this..
webhooks_dict = dict()

# @todo: this should actually be completely rewritten!!! and add webhook avatar change once it changes
# @todo: check if bot has permission to manage webhooks before sending

# webhooks is:
# {
#
#   guild_id: {
#      channel_id: {
#        user_id:  webhook,
#        user_id2: webhook2,
#      }
#   },
#   guild2_id: ...
#
# }

logger = logging.getLogger("red")

# @todo: also, this looks like something which can cause many issues
def webhooks_loaded(guild, channel):
    guild_dict = webhooks_dict.get(guild.id)
    if guild_dict == None:
        return False
    # you can create channel after first loading so we need to check this
    if guild_dict.get(channel.id) == None:
        return False
    return True


async def webhook_send(ctx, channel, user, message=None, file=None, embed=None, wait=True):
    if not webhooks_loaded(ctx.guild, channel):
        await load_webhooks_in_channel(channel)
        asyncio.create_task(load_webhooks(ctx))

    webhook = webhooks_dict.get(ctx.guild.id).get(channel.id).get(str(user.id))
    if webhook == None:
        webhook = await webhook_create(ctx.guild, channel, user)

    try:
        message = await webhook.send(content=message, file=file, embed=embed,
                                     username=user.display_name, wait=wait)
    except (NotFound, AttributeError) as e:  # if for some reason webhook was deleted or has no token
        logger
        webhook = await webhook_create(ctx.guild, channel, user)
        message = await webhook.send(content=message, file=file, embed=embed,
                                     username=user.display_name, wait=wait)

    return message


# @todo: webhook limit in current channel
async def webhook_create(guild, channel, user):
    avatar = await user.avatar_url_as().read()  # returns bytes object
    webhook = await channel.create_webhook(name=user.id, avatar=avatar)
    webhooks_dict[guild.id][channel.id][str(user.id)] = webhook
    return webhook


async def load_webhooks_in_channel(channel):
    if webhooks_dict.get(channel.guild.id) is None:
        webhooks_dict[channel.guild.id] = {}
    if webhooks_dict[channel.guild.id].get(channel.id) is not None:
        return
    webhooks_dict[channel.guild.id][channel.id] = dict()
    webhooks = await channel.webhooks()
    for webhook in webhooks:
        if webhook.token is None:
            continue
        webhooks_dict[channel.guild.id][channel.id][webhook.name] = webhook


async def load_webhooks(ctx):
    webhooks_dict[ctx.guild.id] = dict()
    for channel in ctx.guild.text_channels:
        if not channel.permissions_for(ctx.me).manage_webhooks:
            continue
        await load_webhooks_in_channel(channel)
