from .baseListener import Listener
from .listenerType import ListenerType
from sleekxmpp import ClientXMPP

from pprint import pprint

class JabberListener(Listener):

    listenerType = ListenerType.JABBER

    def __init__(self, jid, password, host, port):
        print("Client for: " + jid)
        self.client =  ClientXMPP(jid, password)
        self.client.add_event_handler("session_start", self.onConnect)
        self.client.add_event_handler("message", self.parseMessage)
        self.host = host
        self.port = port

    def connect(self):
        print("Connecting... " + self.host + ":" + str(self.port))
        self.client.connect((self.host, self.port))
        self.client.process()

    def onConnect(self, event):
        self.client.send_presence()
        print("Connected")
        pprint(event)

    def parseMessage(self, msg):
        if self.messageHandler is None:
            return

        self.messageHandler(msg)
