from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message
from Resources.Status import Status
import discord
from discord import User

from datetime import datetime
import asyncio
import threading
import time

import logging
_log = logging.getLogger("PingRelay")

class DiscordListener(Listener):

    listenerType = ListenerType.DISCORD

    def __init__(self, config):
        super().__init__(config)
        self.email = config["email"]
        self.password = config["password"]
        self.name = config["name"]
        self.client = discord.Client()
        _log.info("{0} - Initializing Discord client".format(self.name))

    def connect(self):
        _log.info("{0} - Signing into Discord with user {1}".format(self.name, self.email))
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.clientLoop = asyncio.get_event_loop()
        self.clientLoop.run_until_complete(self.runDiscord())

    async def runDiscord(self):
        try:
            await self.client.start(self.email, self.password)
        except Exception as err:
            logging.warn("{0} - Discord has disconnected".format(self.name))

    async def on_ready(self):
        _log.info("{0} - Connected to discord".format(self.name))

    async def on_message(self, message):

        _log.debug("{0} - Got message from discord {1}".format(self.name, message.content))
        if self.messageHandler is None:
            return

        if message.content is None:
            return

        sender = message.author.display_name
        if message.channel.is_private:
            channel = "Direct Message"
            server = "Discord"
        else:
            channel = message.channel.name
            server = message.channel.server
        text = message.content
        sent_at = message.timestamp
        msg = Message(self, text, sender, channel, server, sent_at)

        self.messageHandler(msg)
