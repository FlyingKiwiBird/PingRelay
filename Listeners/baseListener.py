from Resources.ThreadedService import ThreadedService

class Listener(ThreadedService):



    def __init__(self, config):
        super(Listener, self).__init__()
        self.config = config
        self.listenerType = None
        self.client = None
        self.name = None
        self.messageHandler = None
        self.connectionType = ServiceType.LISTENER

    def on_message_received(self, messageHandler):
        self.messageHandler = messageHandler

        def __str__(self):
            if self.name is not None:
                return self.name
            return "Unknown"
