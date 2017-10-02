from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message

import time

import logging
_log = logging.getLogger("PingRelay")

class MockListener(Listener):

    listenerType = ListenerType.DISCORD

    def __init__(self, config):
        super(MockListener, self).__init__(config)
        self.running = False
        self.name = config["name"]
        self.intv = config["interval"]
        self.enabled = config["enabled"]

        self.message = config["message"]
        self.server = config["server"]
        self.channel = config["channel"]
        self.sender = config["sender"]
        _log.debug("{0} - Setup mock listener".format(self.name))

    def run(self):
        self.running = self.enabled
        _log.debug("{0} - Mocking started".format(self.name))
        self.loop()

    def stop(self):
        self.autoreconnect = False
        self.running = False

    def loop(self):
        while self.running:
            message = Message(self, self.message, self.sender, self.channel, self.server)
            self.messageHandler(message)
            time.sleep(self.intv)
        super(MockListener, self).finished()
