import sys
import time
import threading

from Resources.ThreadedService import ThreadStatus
from Resources.ServiceType import ServiceType

import logging
_log = logging.getLogger("PingRelay")

class Reconnect(threading.Thread):
    def __init__(self, application, config):
        threading.Thread.__init__(self)
        self.app = application
        self.config = config
        if "reconnect_time" in self.config:
            self.interval = self.config["reconnect_time"]
        else:
            self.interval = 10

    def run(self):
        while(True):
            _log.debug("Checking for DC services")
            #Reconnect emitters
            for emitter in self.app.emitters:
                if emitter.status() == ThreadStatus.Complete:
                    if emitter.autoreconnect:
                        self.app.reconnect_emitter(emitter)

            #Reconnect listeners
            for listener in self.app.listeners:
                if listener.status() == ThreadStatus.Complete:
                    if listener.autoreconnect:
                        self.app.reconnect_listener(listener)

            #Wait
            time.sleep(self.interval)
