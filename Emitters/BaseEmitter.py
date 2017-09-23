from Resources.ThreadedService import ThreadedService

class Emitter(ThreadedService):

    emitType = None
    name = None

    def __init__(self, config):
        super(Emitter, self).__init__()
        self.config = config
        self.outbox = []

    def emit(self, message):
        self.outbox.append(message)
