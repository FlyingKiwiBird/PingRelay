from .BaseEmitter import Emitter
from .EmitterType import EmitterType

import time

import logging
_log = logging.getLogger("PingRelay")

class CliEmitter(Emitter):

    emitterType = EmitterType.CLI

    def __init__(self, config, alertOnly):
        super(CliEmitter, self).__init__(config, alertOnly)
        self.online = True
        _log.debug("CLI emitter started")

    def run(self):
        delay = 10
        while self.online:
            if self.outbox:
                for message in self.outbox:
                    print(message)
                del self.outbox [:]
            time.sleep(delay)

    def stop(self):
        self.autoreconnect = False
        self.online = False

    def emit(self, message):
        _log.debug("Got message: '{0}'".format(message))
        print(message)
