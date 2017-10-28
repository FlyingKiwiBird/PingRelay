from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message
from sleekxmpp import ClientXMPP
import re
import logging
_log = logging.getLogger("PingRelay")

from pprint import pprint

__name__ = "JabberListener"

class JabberListener(Listener):

    listenerType = ListenerType.JABBER

    def __init__(self, config):
        super(JabberListener, self).__init__(config)

        self.name = config['name']
        self.jid = config['jid']
        self.password = config['password']
        self.host = config['host']
        self.port = config['port']

        jid_parts = self.jid.split("@")
        self.nick = jid_parts[0]

        if "pm_list" in config:
            self.pm_list = config["pm_list"]
            self.pm_filter = True
        else:
            self.pm_list = []
            self.pm_filter = False

        if "filter_list" in config:
            self.filter_list = config["filter_list"]
            self.filter = True
        else:
            self.filter_list = []
            self.filter = False

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
        super(JabberListener, self).finished()

    def stop(self):
        _log.info("Stopping Jabber")
        self.autoreconnect = False
        self.client.disconnect(wait=True)

    def onConnect(self, event):
        self.client.sendPresence()
        _log.info("{0} - Connected to: {1}:{2}".format(self.name, self.host, self.port))
        self.joinRooms()

    def joinRooms(self):
        if "channel_list" not in self.config:
            return
        rooms = self.config["channel_list"]
        for r in rooms:
            room_addr = "{0}@{1}".format(r, self.host)
            _log.debug("{0} - Attempting to join {1} as {2}".format(self.name, room_addr, self.nick))
            self.client.plugin['xep_0045'].joinMUC(room_addr, self.nick)

    def onDisconnect(self, event):
        _log.warning("{0} - Disconnected from: {1}:{2}".format(self.name, self.host, self.port))

    def parseMessage(self, msg):
        try:
            _log.debug("{0} - Got message from Jabber: {1}".format(self.name, msg))
        except Exception:
            _log.debug("{0} - Got message from Jabber: (Can't display)".format(self.name))
        if self.messageHandler is None:
            return

        msgText = msg["body"]
        #Normal is default
        if "type" not in msg:
            msg["type"] = "normal"

        if msg["type"] == "chat" or msg["type"] == "normal":
            msgChannel = "Direct Message"
            msgFromParts = msg["from"].bare.split("@")
            msgFrom = msgFromParts[0]
            #PM filter
            if self.pm_filter:
                if msgFrom not in self.pm_list:
                    _log.debug("{0} - Sender not in PM list, ignore".format(self.name))
                    return

            #text filter
            if not self.textFilter(msgText):
                 _log.debug("{0} - Message does not match a text filter, ignore".format(self.name))
                 return

        elif msg["type"] == "groupchat":
            msgChannelParts = msg["mucroom"].split("@")
            msgChannel = msgChannelParts[0]
            msgFrom = msg["mucnick"]
        else:
            _log.warn("{0} - Unknown message type from Jabber: {1}\n{2}".format(self.name, msg["type"], msg))

        message = Message(self, msgText, msgFrom, msgChannel, self.host)
        self.relay_message(message)

    def textFilter(self, text):
        if not self.filter:
            return True
        for f in self.filter_list:
            filter_re = re.compile(f)
            if filter_re.search(text) is not None:
                return True
        return False
