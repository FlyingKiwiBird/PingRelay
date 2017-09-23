from .BaseEmitter import Emitter
from .EmitterType import EmitterType

import asyncio
import discord

import logging
_log = logging.getLogger("PingRelay")

class DiscordEmitter(Emitter):

    emitterType = EmitterType.DISCORD

    def __init__(self, config):
        super(DiscordEmitter, self).__init__(config)
        self.token = config["token"]
        self.name = config["name"]
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client = discord.Client(loop=self.loop)
        _log.info("{0} - Initializing Discord client".format(self.name))

    def stop(self):
        _log.info("Stopping Discord")
        asyncio.run_coroutine_threadsafe(self.client.logout(), self.loop)

    def run(self):
        _log.info("{0} - Signing into Discord with bot".format(self.name))
        self.client.event(self.on_ready)
        self.loop.run_until_complete(self.runDiscord())
        super(DiscordEmitter, self).finished()

    async def runDiscord(self):
        try:
            await self.client.start(self.token)
        except Exception as err:
            logging.warn("{0} - Discord has disconnected: {1}".format(self.name, err))

    async def on_ready(self):
        _log.info("{0} - Connected to discord".format(self.name))

    async def send_message(self, message):
        #Temp for testing
        channel = self.client.get_channel("361034679618502656")
        await self.client.send_message(channel, content=message)

    def emit(self, message):
        asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
