from Listeners.JabberListener import JabberListener
from Listeners.SlackListener import SlackListener
from Listeners.DiscordListener import DiscordListener
from Listeners.MockListener import MockListener
from Listeners.ListenerType import ListenerType

from Emitters.EmitterType import EmitterType
from Emitters.CliEmitter import CliEmitter
from Emitters.DiscordEmitter import DiscordEmitter

from pprint import pprint
from datetime import datetime

import os
import logging
import time

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

    #This little guy makes the whole thing tick
    def relay(self, msg):
        for e in self.emitters:
            e.emit(msg)

    def startListeners(self, listeners):
        for l in listeners:
            try:
                listener = self.generateListener(l)
                if listener is None:
                    continue
                listener.start()
                self.listeners.append(listener)
            except Exception as err:
                _log.error("Could not start listener '{0}': {1}".format(l, err))
                continue

    def generateListener(self, config):
        listenType = ListenerType[config['type'].upper()]
        listener = None
        if(listenType == ListenerType.JABBER):
            listener = JabberListener(config)
        elif(listenType == ListenerType.SLACK):
            listener = SlackListener(config)
        elif(listenType == ListenerType.DISCORD):
            listener = DiscordListener(config)
        elif (listenType == ListenerType.MOCK):
            listener = MockListener(config)
        else:
            return None
        listener.on_message_received(self.relay)
        listener.on_stop(self.listener_closed)
        return listener


    def startEmitters(self, emitters):
        for e in emitters:
            try:
                emitter = generateEmitter(e)
                if emitter is None:
                    continue
                emitter.start()
                self.emitters.append(emitter)
            except Exception as err:
                if "name" in e:
                    e_name = e['name']
                else:
                    e_name = "Unknown"
                _log.error("Could not start emitter'{0}': {1}".format(e_name, err))
                continue

    def generateEmitter(self, config):
        emitter = None
        emitterType = EmitterType[config['type'].upper()]
        if(emitterType == EmitterType.CLI):
            emitter = CliEmitter(config)
        elif(emitterType == EmitterType.DISCORD):
            emitter = DiscordEmitter(config)
        return emitter

    def listener_closed(self, listener):
        _log.error("A listener was closed - {0}".format(listener.name))

        if not listener.autoreconnect:
            return

        time.delay(10)
        _log.info("Attempting to reconnect - {0}".format(emitter.name))

        #Grab the config and delete the old listener
        config = listener.config
        for i, l in enumerate(self.listeners):
            if l == listener:
                del self.listeners[i]
                break

        #Start a new listener in its place
        try:
            listener = self.generateListener(config)
            listener.start()
            self.listeners.append(listener)
        except Exception as err:
            _log.error("Could not start listener '{0}': {1}".format(l, err))

    def emitter_closed(self, emitter):
        _log.error("A emitter was closed - {0}".format(emitter.name))

        if not emitter.autoreconnect:
            return

        time.delay(10)
        _log.info("Attempting to reconnect - {0}".format(emitter.name))
        #Grab the config and delete the old listener
        config = emitter.config
        for i, e in enumerate(self.emitter):
            if e == emitter:
                del self.emitter[i]
                break

        #Start a new listener in its place
        try:
            emitter = self.generateListener(config)
            emitter.start()
            self.listeners.append(emitter)
        except Exception as err:
            _log.error("Could not start listener '{0}': {1}".format(l, err))
