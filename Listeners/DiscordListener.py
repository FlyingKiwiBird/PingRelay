from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message

import discord
from discord import User

from pprint import pprint
from datetime import datetime
import asyncio
import threading
import time
import re

import logging
_log = logging.getLogger("PingRelay")

class DiscordListener(Listener):

    listenerType = ListenerType.DISCORD

    def __init__(self, config):
        super(DiscordListener, self).__init__(config)
        self.email = config["email"]
        self.password = config["password"]
        self.name = config["name"]
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client = discord.Client(loop=self.loop)
        _log.info("{0} - Initializing Discord client".format(self.name))

    def run(self):
        _log.info("{0} - Signing into Discord with user {1}".format(self.name, self.email))
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.loop.run_until_complete(self.runDiscord())
        super(DiscordListener, self).finished()

    def stop(self):
        _log.info("Stopping Discord")
        asyncio.run_coroutine_threadsafe(self.client.logout(), self.loop)

    async def runDiscord(self):
        try:
            await self.client.start(self.email, self.password)
        except Exception as err:
            logging.warn("{0} - Discord has disconnected: {1}".format(self.name, err))

    async def on_ready(self):
        _log.info("{0} - Connected to discord".format(self.name))

    async def on_message(self, message):
        try:
            _log.debug("{0} - Got message from discord: \"{1}\"".format(self.name, message.content))
        except Exception:
            _log.debug("{0} - Got message from discord: (can't display)")
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
            #Server filter
            if "servers" in self.config:
                if server not in self.config["servers"]:
                    return

        #replace usernames
        text = self.get_names_from_mentions(message)

        sent_at = message.timestamp
        msg = Message(self, text, sender, channel, server, sent_at)

        self.messageHandler(msg)

    def get_names_from_mentions(self, message):
        mentions = message.mentions
        text = message.content
        matches = re.finditer(r"<@[^\d]?(\d+)>", text)

        for match in matches:
            full_match = match.group()
            user_id = match.group(1)
            user = next((mention for mention in mentions if mention.id == user_id), user_id)
            text = text.replace(full_match, "@" + user.display_name)

        return text
