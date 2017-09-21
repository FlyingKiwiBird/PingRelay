from Resources.Status import Status

class Listener:

    listenerType = None
    client = None
    config = None
    messageHandler = None
    status = Status.DISCONNECTED

    def __init__(self, config):
        self.config = config

    def connect(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def status(self):
        return self.status

    def onMessage(self, messageHandler):
        self.messageHandler = messageHandler
