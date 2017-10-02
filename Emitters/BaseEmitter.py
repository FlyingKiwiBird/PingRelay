from Resources.ThreadedService import ThreadedService
from Resources.ServiceType import ServiceType

class Emitter(ThreadedService):



    def __init__(self, config, alertOnly = False):
        super(Emitter, self).__init__()
        self.config = config
        self.alertOnly = alertOnly
        self.outbox = []
        self.emitType = None
        self.name = None
        self.alertOnly = False
        self.connectionType = ServiceType.EMITTER

    def emit(self, message):
        self.outbox.append(message)
