from Listeners.JabberListener import JabberListener
from Listeners.SlackListener import SlackListener
from Listeners.DiscordListener import DiscordListener
from Listeners.ListenerType import ListenerType

from Emitters.EmitterType import EmitterType
from Emitters.CliEmitter import CliEmitter

from pprint import pprint
from datetime import datetime

import os
import logging

_log = logging.getLogger("PingRelay")

class App():

    def __init__(self, config):
        self.config = config


    def run(self):

        self.emitters = []
        if 'emitters' in self.config:
            self.startEmitters(self.config['emitters'])

        self.listeners = []
        if 'listeners' in self.config:
            self.startListeners(self.config['listeners'])



    def startListeners(self, listeners):
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
                listener.onMessage(self.relay)
                listener.start()
                self.listeners.append(listener)
            except Exception as err:
                if "name" in l:
                    l_name = l['name']
                else:
                    l_name = "Unknown"
                _log.error("Could not start listener '{0}': {1}".format(l_name, err))
                pass

    def startEmitters(self, emitters):
        for e in emitters:
            try:
                emitter = None
                emitterType = EmitterType[e['type'].upper()]
                if(emitterType == EmitterType.CLI):
                    emitter = CliEmitter(e)
                else:
                    pass
                emitter.start()
                self.emitters.append(emitter)
            except Exception as err:
                if "name" in e:
                    e_name = e['name']
                else:
                    e_name = "Unknown"
                _log.error("Could not start emitter'{0}': {1}".format(e_name, err))
                pass

    def relay(self, msg):
        for e in self.emitters:
            e.emit(msg)
