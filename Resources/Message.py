from datetime import datetime

class Message:

    def __init__(self, listener, message, sender, channel, server, time = datetime.now()):
        self.listener = listener
        self.message = message
        self.sender = sender
        self.channel = channel
        self.server = server
        self.time = time

    def __str__(self):
        time_str = self.time.strftime("%Y-%m-%d %I:%M:%S %p")
        return "[{0}] {1}>{2}>{3}: {4}".format(time_str, self.server, self.channel, self.sender, self.message)
