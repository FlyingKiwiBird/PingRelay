from Resources.ThreadedService import ThreadedService

class Emitter(ThreadedService):

    emitType = None
    name = None
    alertOnly = False

    def __init__(self, config, alertOnly = False):
        super(Emitter, self).__init__()
        self.config = config
        self.alertOnly = alertOnly
        self.outbox = []

    def emit(self, message):
        self.outbox.append(message)
