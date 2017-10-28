from Resources.ThreadedService import ThreadedService
from Resources.ServiceType import ServiceType

class Emitter(ThreadedService):



    def __init__(self, config, alertOnly = False):
        super(Emitter, self).__init__(config)
        self.alertOnly = alertOnly
        self.emitType = None
        self.name = None
        self.connectionType = ServiceType.EMITTER
        self.messages = 0

    def emit(self, message):
        self.messages += 1
        self.send_message(message)

    def send_message(self, message):
        raise NotImplementedError()
