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
import re

_log = logging.getLogger("PingRelay")

class App():

    def __init__(self, config):
        self.messages = 0
        self.config = config
        if "only_relay_alerts" in config:
            self.alertsOnly = config["only_relay_alerts"]
        else:
            self.alertsOnly = False

        self.alerts = []
        if "alerts" in config:
            self.alerts = config["alerts"]
            _log.debug("Got alerts config: {0}".format(self.alerts))

    def run(self):

        self.emitters = []
        if 'emitters' in self.config:
            self.start_emitters(self.config['emitters'])

        self.listeners = []
        if 'listeners' in self.config:
            self.start_listeners(self.config['listeners'])

    #This little guy makes the whole thing tick
    def relay(self, msg):
        self.check_alerts(msg)
        if self.alertsOnly:
            if not msg.has_alert:
                return
        self.messages += 1
        for e in self.emitters:
            e.emit(msg)

    def check_alerts(self, message):
        _log.debug("Checking message for alerts: '{0}'".format(message.message))
        if "alerts" in message.listener.config:
            all_alerts = self.alerts + message.listener.config["alerts"]
        else:
            all_alerts = self.alerts
        for alert in all_alerts:
            alert_re = re.compile(alert["filter"])
            if alert_re.search(message.message) is not None:
                _log.debug("Matched alert {0}".format(alert["name"]))
                message.add_alert(alert["name"])

############### Initializers

    def start_listeners(self, listeners):
        for l in listeners:
            try:
                listener = self.generate_listener(l)
                if listener is None:
                    continue
                listener.start()
                self.listeners.append(listener)
            except Exception as err:
                _log.error("Could not start listener '{0}': {1}".format(l, err))
                continue

    def start_emitters(self, emitters):
        for e in emitters:
            try:
                emitter = self.generate_emitter(e)
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

########## Generators

    def generate_listener(self, config):
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
        return listener

    def generate_emitter(self, config):
        emitter = None
        emitterType = EmitterType[config['type'].upper()]
        if(emitterType == EmitterType.CLI):
            emitter = CliEmitter(config, self.alertsOnly)
        elif(emitterType == EmitterType.DISCORD):
            emitter = DiscordEmitter(config, self.alertsOnly)
        return emitter

################ Reconnect

    def reconnect_listener(self, listener):
        _log.info("Attempting to reconnect - {0}".format(listener.name))

        #Grab the config and delete the old listener
        config = listener.config
        for i, l in enumerate(self.listeners):
            if l == listener:
                del self.listeners[i]
                break

        #Start a new listener in its place
        try:
            listener = self.generate_listener(config)
            listener.start()
            self.listeners.append(listener)
        except Exception as err:
            _log.error("Could not start listener '{0}': {1}".format(l, err))


    def reconnect_emitter(self, emitter):
        _log.info("Attempting to reconnect - {0}".format(emitter.name))
        #Grab the config and delete the old emitter
        config = emitter.config
        for i, e in enumerate(self.emitters):
            if e == emitter:
                del self.emitters[i]
                break

        #Start a new listener in its place
        try:
            emitter = self.generate_emitter(config)
            emitter.start()
            self.emitters.append(emitter)
        except Exception as err:
            _log.error("Could not start listener '{0}': {1}".format(l, err))
