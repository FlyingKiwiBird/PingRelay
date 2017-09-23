from Listeners.JabberListener import JabberListener
from Listeners.SlackListener import SlackListener
from Listeners.DiscordListener import DiscordListener
from Listeners.ListenerType import ListenerType

from pprint import pprint
from datetime import datetime

import os
import logging

_log = logging.getLogger("PingRelay")

class App():

    def __init__(self, config):
        self.config = config


    def run(self):
        if 'listeners' in self.config:
            self.startListeners(self.config['listeners'])

        if 'relays' in self.config:
            self.startRelays(self.config['relays'])

    def startListeners(self, listeners):
        self.listeners = []
        for l in listeners:
            try:
                listenType = ListenerType[l['type'].upper()]
                listener = None
                if(listenType == ListenerType.JABBER):
                    listener = JabberListener(l)
                elif(listenType == ListenerType.SLACK):
                    listener = SlackListener(l)
                elif(listenType == ListenerType.DISCORD):
                    listener = DiscordListener(l)
                else:
                    pass
                listener.onMessage(self.message)
                listener.start()
                self.listeners.append(listener)
            except Exception as err:
                _log.error("Could not start listener '{0}': {1}".format(l['name'], err))
                pass

    def startRelays(self, relays):
        self.relays = []

    def message(self, msg):
        print(msg)
