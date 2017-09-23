from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message
from sleekxmpp import ClientXMPP

import logging
_log = logging.getLogger("PingRelay")

from pprint import pprint

__name__ = "JabberListener"

class JabberListener(Listener):

    listenerType = ListenerType.JABBER

    def __init__(self, config):
        super().__init__(config)

        self.name = config['name']
        self.jid = config['jid']
        self.password = config['password']
        self.host = config['host']
        self.port = config['port']

        jid_parts = self.jid.split("@")
        self.nick = jid_parts[0]

        _log.info("{0} - Initializing Jabber client for: {1}".format(self.name, self.jid))
        self.client =  ClientXMPP(self.jid, self.password)
        self.client.add_event_handler("session_start", self.onConnect)
        self.client.add_event_handler("disconnected", self.onDisconnect)
        self.client.add_event_handler("message", self.parseMessage)
        self.client.register_plugin("xep_0045")  # Multi-User Chat

    def run(self):
        _log.info("{0} - Connecting to: {1}:{2}".format(self.name, self.host, self.port))
        try:
            self.client.connect((self.host, self.port))
        except Exception as err:
            _log.error("{0} - Connection failed to: {1}:{2}".format(self.name, self.host, self.port))
            return
        self.client.process(block=True)

    def stop(self):
        self.client.disconnect()

    def onConnect(self, event):
        self.client.sendPresence()
        _log.info("{0} - Connected to: {1}:{2}".format(self.name, self.host, self.port))
        self.joinRooms()

    def joinRooms(self):
        rooms = self.config["room_list"]
        for r in rooms:
            room_addr = "{0}@{1}".format(r, self.host)
            _log.debug("{0} - Attempting to join {1} as {2}".format(self.name, room_addr, self.nick))
            self.client.plugin['xep_0045'].joinMUC(room_addr, self.nick)

    def onDisconnect(self, event):
        logging.warning("{0} - Disconnected from: {1}:{2}".format(self.name, self.host, self.port))

    def parseMessage(self, msg):
        _log.debug("{0} - Got message from Jabber: {1}".format(self.name, msg))
        if self.messageHandler is None:
            return

        msgText = msg["body"]
        if msg["type"] == "chat":
            msgChannel = "Direct Message"
            msgFromParts = msg["from"].bare.split("@")
            msgFrom = msgFromParts[0]
        elif msg["type"] == "groupchat":
            msgChannelParts = msg["mucroom"].split("@")
            msgChannel = msgChannelParts[0]
            msgFrom = msg["mucnick"]
        else:
            logging.warn("{0} - Unknown message type from Jabber: {1}".format(self.name, msg["type"]))

        message = Message(self, msgText, msgFrom, msgChannel, self.host)


        self.messageHandler(message)
