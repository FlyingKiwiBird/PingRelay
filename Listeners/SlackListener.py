from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message

from slackclient import SlackClient

from datetime import datetime
import asyncio
import threading
import logging
import time
import re

_log = logging.getLogger("PingRelay")

class SlackListener(Listener):

    listenerType = ListenerType.SLACK

    def __init__(self, config):
        super(SlackListener, self).__init__(config)
        self.running = False

        self.name = config["name"]
        self.token = config["token"]

        if "pm_list" in config:
            self.pm_list = config["pm_list"]
        else:
            self.pm_list = []

        if "channel_list" in config:
            self.channel_list = config["channel_list"]
        else:
            self.channel_list = []

        _log.info("{0} - Initializing Slack client".format(self.name))
        self.client = SlackClient(self.token)
        try:
            server_info = self.client.api_call("team.info")
            self.server = server_info["team"]["name"]
            self.running = True
        except Exception as err:
            _log.warn("{0} - Could not get server name: {1}".format(self.name, err))


    def run(self):
        _log.info("{0} - Connecting to Slack server".format(self.name))
        if self.client.rtm_connect(with_team_state=False):
            _log.info("{0} - Connected to Slack server".format(self.name))
            self.slackRTM()
            super(SlackListener, self).finished()
        else:
            _log.error("{0} - Connection failed".format(self.name))
            self.running = False


    def stop(self):
        _log.info("Stopping slack")
        self.running = False

    def replace_user_id_with_name(self, match):
        user_id = match.group(1)
        try:
            user_info = self.client.api_call("users.info", user=user_id)
            return "@" + user_info["user"]["name"]
        except Exception as err:
            _log.warn("{0} - Could not get user name for {1}".format(self.name, user_id))
            return user_id

    def slackRTM(self):
        delay = 0
        while self.running:
            try:
                events = self.client.rtm_read()
            except Exception as err:
                _log.warn("{0} - Could not get RTM events {1}".format(self.name, err))

            if events:
                delay = 0
                if self.messageHandler is not None:
                    for event in events:
                        if event["type"] == "message":
                            if "text" not in event:
                                continue
                            try:
                                msg = event["text"]
                                _log.debug("{0} - Got message from Slack RTM: {1}".format(self.name, msg))
                            except Exception:
                                _log.debug("{0} - Got message from Slack RTM: (Can't display)".format(self.name))
                            #Get sender
                            try:
                                user_info = self.client.api_call("users.info", user=event["user"])
                                user = user_info["user"]["name"]
                            except Exception as err:
                                _log.warn("{0} - Could not get user info {1}".format(self.name, err))
                                user = "Unknown ({0})".format(event["user"])
                            #Get channel
                            if event["channel"].startswith("C"):
                                try:
                                    channel_info = self.client.api_call("channels.info", channel=event["channel"])
                                    channel = channel_info["channel"]["name"]
                                except Exception as err:
                                    _log.warn("{0} - Could not get channel info {1}".format(self.name, err))
                                    channel = "Unknown ({0})".format(event["channel"])
                                #Channel filter
                                if channel not in self.channel_list:
                                    _log.debug("{0} - Channel '{1}' is not listened to".format(self.name, channel))
                                    continue
                            elif event["channel"].startswith("D"):
                                channel = "Direct Message"
                                #PM Filter
                                if user not in self.pm_list:
                                    _log.debug("{0} - User '{1}' is not listened to".format(self.name, user))
                                    continue
                            #Get time
                            timestamp = float(event["ts"])
                            msgTime = datetime.fromtimestamp(timestamp)

                            #Username replacement
                            regex = re.compile(r"<@([\w\d]+)>")
                            msg = regex.sub(self.replace_user_id_with_name, msg)

                            message = Message(self, msg, user, channel, self.server, msgTime)
                            self.messageHandler(message)

            else:
                delay = min(++delay, 10)
            time.sleep(delay)
        _log.debug("{0} - RTM due to Slack disconnect disconnected".format(self.name))
