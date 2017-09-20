from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message
from sleekxmpp import ClientXMPP
import logging

from pprint import pprint

__name__ = "JabberListener"

class JabberListener(Listener):

    listenerType = ListenerType.JABBER

    def __init__(self, config):
        self.config = config

        self.name = config['name']
        self.jid = config['jid']
        self.password = config['password']
        self.host = config['host']
        self.port = config['port']

        logging.debug("{0} - Initializing Jabber client for: {1}".format(self.name, self.jid))
        self.client =  ClientXMPP(self.jid, self.password)
        self.client.add_event_handler("session_start", self.onConnect)
        self.client.add_event_handler("disconnected", self.onDisconnect)
        self.client.add_event_handler("message", self.parseMessage)
        self.client.register_plugin("xep_0045")  # Multi-User Chat

    def connect(self):
        logging.debug("{0} - Connecting to: {1}:{2}".format(self.name, self.host, self.port))
        try:
            self.client.connect((self.host, self.port))
        except Exception as err:
            logging.error("{0} - Connection failed to: {1}:{2}".format(self.name, self.host, self.port))
            return
        self.client.process()

    def disconnect(self):
        self.client.disconnect()

    def onConnect(self, event):
        self.client.sendPresence()
        logging.debug("{0} - Connected to: {1}:{2}".format(self.name, self.host, self.port))

    def onDisconnect(self, event):
        logging.warning("{0} - Disconnected from: {1}:{2}".format(self.name, self.host, self.port))

    def parseMessage(self, msg):
        logging.debug("{0} - Got message: {1}".format(self.name, msg))
        if self.messageHandler is None:
            return

        message = Message(self, msg["body"], msg["mucnick"], msg["mucroom"])


        self.messageHandler(message)
