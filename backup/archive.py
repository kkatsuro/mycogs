
    @commands.command()
    async def list_available_channels(self, ctx):
        channels = []
        async for guild in self.bot.fetch_guilds():
            for channel in await guild.fetch_channels():
                if not isinstance(channel, discord.TextChannel):
                    continue

                try:
                    async for message in channel.history(limit=1, oldest_first=True):
                        pass
                except discord.Forbidden:
                    continue

                channels.append(channel)

        for a in [f'{channel.name} -- {channel.id}' for channel in channels]:
            asyncio.create_task(ctx.send(a))

        # looks like you can get more channels this way, and display permissions for them
        # but you can't even read them..
        # async for guild in self.bot.fetch_guilds():
        #     for channel in await guild.fetch_channels():
        # for channel in channels:
        #     if channel.id == id:
        #         perms = channel.permissions_for(ctx.me)

        #         await ctx.send('perms:')

        #         message = ''
        #         for attr in dir(perms):
        #             if isinstance(perms.__getattribute__(attr), bool):
        #                 message += f'{attr}: {"✅" if perms.__getattribute__(attr) else "❌"}\n'

        #         await ctx.send(message)

    @commands.command()
    async def steal_message_from(self, ctx, channel_id: int):
        channel = await self.bot.fetch_channel(channel_id)
        perms = channel.permissions_for(ctx.me)

        await ctx.send('perms:')

        message = ''
        for attr in dir(perms):
            if isinstance(perms.__getattribute__(attr), bool):
                message += f'{attr}: {"✅" if perms.__getattribute__(attr) else "❌"}\n'

        await ctx.send(message)

        async for message in channel.history(limit=1, oldest_first=False):
            await ctx.send(message.content)


