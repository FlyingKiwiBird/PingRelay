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
        self.channel = config["default_channel"]
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
        _log.debug("{0} - Got message to emit".format(self.name))
        channel = self.get_channel(message)
        await self.client.send_message(channel, content=message)

    def get_channel(self, message):
        channel_id = self.channel
        if "channels" in self.config:
            for ch in self.config["channels"]:
                if ch["from_server"] == message.server:
                    channel_id = ch["to_channel"]
                    break

        channel = self.client.get_channel(channel_id)
        if channel is None:
            _log.error("{0} - The channel ID '{1}' is not valid".format(self.name, channel_id))
            #Fallbak to default channel
            if channel_id != self.channel:
                channel = self.client.get_channel(self.channel)

        return channel




    def emit(self, message):
        asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
