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
        if "reconnect_interval" in self.config:
            self.interval = self.config["reconnect_interval"]
        else:
            self.interval = 10

    def run(self):
        while(True):
            #Reconnect emitters
            for emitter in self.app.emitters:
                if emitter.status() == ThreadStatus.Complete:
                    if emitter.autoreconnect:
                        self.app.reconnect_emitter(emitter)
                else:
                    self.autorestart(emitter)



            #Reconnect listeners
            for listener in self.app.listeners:
                if listener.status() == ThreadStatus.Complete:
                    if listener.autoreconnect:
                        self.app.reconnect_listener(listener)
                else:
                    self.autorestart(listener)

            #Wait
            time.sleep(self.interval)

    def autorestart(self, service):
        if "autorestart_interval" in service.config:
            restart_intv = service.config["autorestart_interval"]
            uptime = service.uptime()
            uptime_seconds = uptime.total_seconds()
            if  uptime_seconds >= restart_intv:
                _log.info("Auto restarting service: '{0}' it was alive for {1}".format(service, uptime))
                service.stop()
                self.app.reconnect_service(service)
                return True
        return False
