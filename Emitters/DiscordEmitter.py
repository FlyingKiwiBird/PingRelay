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
        self.token = config["token"]
        self.name = config["name"]
        self.channel = config["default_channel"]
        if "alert_channel" in config:
            self.alert_channel = config["alert_channel"]
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client = discord.Client(loop=self.loop)
        if "format" in config:
            if "time_format" in config:
                self.formatter = MessageFormatter(config["format"], config["time_format"])
            else:
                self.formatter = MessageFormatter(config["format"])

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
        channels = self.get_channels(message)
        _log.debug("{0} - Sending message to {1} channels".format(self.name, str(len(channels))))
        #Replace @here and @everyone
        regex = r"@(everyone|here)"
        subst = r"`@\1`"
        message.message = re.sub(regex, subst, message.message)
        #formatter
        if self.formatter is not None:
            message_str = self.formatter.format_message(message)
        else:
            message_str = str(message)
        #alerts
        if message.has_alert and not self.alertOnly:
            alert_str = "@everyone this message matched alert(s): " + message.get_alert_str() + "\n"
            message_str = alert_str + message_str

        for channel in channels:
            try:
                await self.client.send_message(channel, content=message_str)
                _log.debug("{0} - Sent message to channel '{1}' on '{2}'".format(self.name, channel.name, channel.server.name))
            except Exception as err:
                _log.error("{0} - Could not send message: {1}".format(self.name, err))

    def get_channels(self, message):
        default_channel_id = self.channel
        channel_list = []
        alert = False

        if self.alert_channel is not None:
            if message.has_alert:
                channel_list.append(self.alert_channel)
                alert = True

        if not alert:
            if "channels" in self.config:
                for ch in self.config["channels"]:
                    if message.server in ch["from_server_list"]:
                        channel_list = ch["to_channel_list"]
                        break

        channels = []
        for channel_id in channel_list:
            channel = self.client.get_channel(channel_id)
            if channel is None:
                _log.error("{0} - The channel ID '{1}' is not valid".format(self.name, channel_id))
            else:
                channels.append(channel)

        #Send to default if no match
        if(len(channels) == 0):
            channel = self.client.get_channel(default_channel_id)
            if channel is None:
                _log.error("{0} - The default channel (ID = '{1}') is not valid".format(self.name, default_channel_id))
            else:
                channels.append(channel)

        return channels




    def emit(self, message):
        asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
