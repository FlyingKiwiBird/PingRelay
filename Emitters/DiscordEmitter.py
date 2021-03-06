from .BaseEmitter import Emitter
from .EmitterType import EmitterType
from Resources.MessageFormatter import MessageFormatter

import asyncio
import discord
import re

import logging
_log = logging.getLogger("PingRelay")

class DiscordEmitter(Emitter):

    emitterType = EmitterType.DISCORD
    formatter = None
    alert_channel = None

    def __init__(self, config, alertOnly):
        super(DiscordEmitter, self).__init__(config, alertOnly)
        self.token = config.get("token")
        self.name = config.get("name")
        self.channel = config.get("default_channel")
        self.alert_channel = config.get("alert_channel")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client = discord.Client(loop=self.loop)
        if "format" in config:
            if "time_format" in config:
                self.formatter = MessageFormatter(config.get("format"), config.get("time_format"))
            else:
                self.formatter = MessageFormatter(config.get("format"))

        self.use_embed = config.get("use_embed", True)
        _log.info("{0} - Initializing Discord client".format(self.name))

    def stop(self):
        _log.info("Stopping Discord")
        self.autoreconnect = False
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

    async def send_message_async(self, message):
        _log.debug("{0} - Got message to emit".format(self.name))
        channels = self.get_channels(message)
        _log.debug("{0} - Sending message to {1} channels".format(self.name, str(len(channels))))
        #Replace @here and @everyone
        regex = r"@(everyone|here)"
        subst = r"`@\1`"
        message.message = re.sub(regex, subst, message.message)
        _log.debug("{0} - Replaced @ command".format(self.name))
        #formatter
        if self.use_embed:
            pass
        elif self.formatter is not None:
            message_str = self.formatter.format_message(message)
            _log.debug("{0} - Formatted string".format(self.name))
        else:
            message_str = str(message)

        for channel in channels:
            try:
                if self.use_embed:
                    content = None
                    if message.has_alert:
                        content = "@everyone"
                    _log.debug("Using embed method")
                    await channel.send(content=content, embed=message.embed())
                else:
                    _log.debug("Using text method")
                    await channel.send(content=message_str)
                _log.debug("{0} - Sent message to channel '{1}' on '{2}'".format(self.name, channel.name, channel.server.name))
            except Exception as err:
                _log.error("{0} - Could not send message: {1}".format(self.name, err))

    def get_channels(self, message):
        default_channel_id = self.channel
        channel_list = []
        alert = False

        #If alert channel is set, use it
        if self.alert_channel is not None:
            if message.has_alert:
                channel_list.append(self.alert_channel)
                alert = True
        
        #Otherwise get it from the channel list
        if not alert:
            if "channels" in self.config:
                for ch in self.config["channels"]:
                    if message.server in ch["from_server_list"]:
                        #Check if there is a channel filter
                        ch_filter = ch.get("from_channel_filter")
                        if ch_filter:
                            if message.channel in ch_filter:
                                channel_list.extend(ch["to_channel_list"])
                        else:
                            channel_list.extend(ch["to_channel_list"])

        #Get channel from the channel id
        channels = []
        for channel_id in channel_list:
            channel = self.client.get_channel(int(channel_id))
            if channel is None:
                _log.error("{0} - The channel ID '{1}' is not valid".format(self.name, channel_id))
            else:
                channels.append(channel)

        #Send to default if no match
        if default_channel_id is not None:
            if(len(channels) == 0):
                channel = self.client.get_channel(int(default_channel_id))
                if channel is None:
                    _log.error("{0} - The default channel (ID = '{1}') is not valid".format(self.name, default_channel_id))
                else:
                    channels.append(channel)

        return channels




    def send_message(self, message):
        asyncio.run_coroutine_threadsafe(self.send_message_async(message), self.loop)
