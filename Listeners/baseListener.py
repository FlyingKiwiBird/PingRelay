from Resources.ThreadedService import ThreadedService
from Resources.ServiceType import ServiceType

class Listener(ThreadedService):



    def __init__(self, config):
        super(Listener, self).__init__()
        self.config = config
        self.listenerType = None
        self.client = None
        self.name = None
        self.messageHandler = None
        self.connectionType = ServiceType.LISTENER
        self.messages = 0

    def on_message_received(self, messageHandler):
        self.messageHandler = messageHandler

    def relay_message(self, message):
        if self.messageHandler is not None:
            self.messages += 1
            self.messageHandler(message)


    def __str__(self):
        if self.name is not None:
            return self.name
        return "Unknown"
