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

    def on_message_received(self, messageHandler):
        self.messageHandler = messageHandler

        def __str__(self):
            if self.name is not None:
                return self.name
            return "Unknown"
