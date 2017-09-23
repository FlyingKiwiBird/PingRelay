from Resources.ThreadedService import ThreadedService

class Listener(ThreadedService):

    listenerType = None
    client = None
    config = None
    name = None
    messageHandler = None

    def __init__(self, config):
        super(Listener, self).__init__()
        self.config = config

    def onMessage(self, messageHandler):
        self.messageHandler = messageHandler
