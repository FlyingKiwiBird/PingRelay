import threading

class Emitter(threading.Thread):

    emitType = None
    name = None

    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config
        self.outbox = []

    def run(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def emit(self, message):
        self.outbox.append(message)
