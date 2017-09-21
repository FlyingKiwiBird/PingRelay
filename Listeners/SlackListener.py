from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message
from Resources.Status import Status
from slackclient import SlackClient

from datetime import datetime
import asyncio
import threading
import logging
import time

class SlackListener(Listener):

    listenerType = ListenerType.SLACK

    def __init__(self, config):
        super().__init__(config)

        self.name = config["name"]
        self.token = config["token"]

        logging.info("{0} - Initializing Slack client".format(self.name))
        self.client = SlackClient(self.token)

    def connect(self):
        logging.info("{0} - Connecting to Slack server".format(self.name))
        if self.client.rtm_connect(with_team_state=False):
            logging.info("{0} - Connected to Slack server".format(self.name))
            self.slackService = threading.Thread(target=self.slackRTM)
            self.status = Status.CONNECTED
            self.slackService.start()
        else:
            logging.error("{0} - Connection failed".format(self.name))
            self.status = Status.DISCONNECTED

    def slackRTM(self):
        delay = 0
        while self.status == Status.CONNECTED:
            try:
                events = self.client.rtm_read()
            except Exception as err:
                logging.warn("{0} - Could not get RTM events {1}".format(self.name, err))

            if events:
                delay = 0
                if self.messageHandler is not None:
                    for event in events:
                        if event["type"] == "message":
                            if "text" not in event:
                                pass
                            msg = event["text"]
                            logging.debug("{0} - Got message from Slack RTM: {1}".format(self.name, event))
                            #Get sender
                            try:
                                user_info = self.client.api_call("users.info", user=event["user"])
                                user = user_info["user"]["name"]
                            except Exception as err:
                                logging.warn("{0} - Could not get user info {1}".format(self.name, err))
                                user = "Unknown ({0})".format(event["user"])
                            #Get channel
                            if event["channel"].startswith("C"):
                                try:
                                    channel_info = self.client.api_call("channels.info", channel=event["channel"])
                                    channel = channel_info["channel"]["name"]
                                except Exception as err:
                                    logging.warn("{0} - Could not get channel info {1}".format(self.name, err))
                                    channel = "Unknown ({0})".format(event["channel"])
                            elif event["channel"].startswith("D"):
                                channel = "Direct Message"
                            #Get time
                            timestamp = float(event["ts"])
                            msgTime = datetime.fromtimestamp(timestamp)

                            message = Message(self, msg, user, channel, msgTime)
                            self.messageHandler(message)

            else:
                delay = min(++delay, 10)
            time.sleep(delay)
        logging.debug("{0} - RTM due to Slack disconnect disconnected".format(self.name))
