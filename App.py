from Listeners.JabberListener import JabberListener
from Listeners.SlackListener import SlackListener
from Listeners.MockListener import MockListener
from Listeners.ListenerType import ListenerType

from Emitters.EmitterType import EmitterType
from Emitters.CliEmitter import CliEmitter
from Emitters.DiscordEmitter import DiscordEmitter

from Resources.ServiceType import ServiceType
from Resources.Anonymizer import anonymize

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

        self.always_alert = config.get("always_alert", False)
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
        anonymize(msg)
        self.check_alerts(msg)
        _log.info("Relaying message: {0}".format(msg))
        if self.alertsOnly:
            if not msg.has_alert:
                return
        self.messages += 1
        for e in self.emitters:
            e.emit(msg)

    def check_alerts(self, message):
        if self.always_alert:
            message.add_alert("Perpetual")
        if "alerts" in message.listener.config:
            all_alerts = self.alerts + message.listener.config["alerts"]
        else:
            all_alerts = self.alerts
        for alert in all_alerts:
            alert_re = re.compile(alert["filter"], re.IGNORECASE)
            if alert_re.search(message.search_text) is not None:
                _log.debug("Matched alert {0}".format(alert["name"]))
                message.add_alert(alert["name"])

############### Initializers

    def start_listeners(self, listeners):
        for l in listeners:
            try:
                listener = self.generate_listener(l)
                if listener is None:
                    _log.error("Bad listener format: {0}".format(l))
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

    def reconnect_service(self, service):
        if service.connectionType == ServiceType.LISTENER:
            self.reconnect_listener(service)
        elif service.connectionType == ServiceType.EMITTER:
            self.reconnect_emitter(service)

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
            _log.error("Could not start listener '{0}': {1}".format(e, err))
