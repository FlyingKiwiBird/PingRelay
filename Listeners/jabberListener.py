from .baseListener import Listener
from .listenerType import ListenerType
from sleekxmpp import ClientXMPP

from pprint import pprint

class JabberListener(Listener):

    listenerType = ListenerType.JABBER

    def __init__(self, config):
        self.config = config
        self.name = config['name']
        self.jid = config['jid']
        self.password = config['password']
        self.host = config['host']
        self.port = config['port']
        self.client =  ClientXMPP(self.jid, self.password)
        self.client.add_event_handler("session_start", self.onConnect)
        self.client.add_event_handler("message", self.parseMessage)
        self.client.register_plugin("xep_0045")  # Multi-User Chat

    def connect(self):
        print("Connecting... " + self.host + ":" + str(self.port))
        try:
            self.client.connect((self.host, self.port))
        except Exception as err:
            print("Could not connect to Jabber host: {0}".format(err))
        self.client.process()

    def disconnect(self):
        self.client.disconnect()

    def onConnect(self, event):
        self.client.sendPresence()
        print("Connected")
        pprint(event)

    def parseMessage(self, msg):
        print("Got message")
        if self.messageHandler is None:
            return

        self.messageHandler(msg)
