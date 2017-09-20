
class Listener:

    listenerType = None
    client = None
    messageHandler = None

    def connect(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def status(self):
        raise NotImplementedError()

    def onMessage(self, messageHandler):
        self.messageHandler = messageHandler
