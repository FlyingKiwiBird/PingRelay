import threading

class Listener(threading.Thread):

    listenerType = None
    client = None
    config = None
    name = None
    messageHandler = None

    def __init__(self, config):
        threading.Thread.__init__(self)
        self.config = config

    def run(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def onMessage(self, messageHandler):
        self.messageHandler = messageHandler
