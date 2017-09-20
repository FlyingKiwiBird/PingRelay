from datetime import datetime

class Message:

    def __init__(self, listener, message, sender, channel, time = datetime.now()):
        self.listener = listener
        self.message = message
        self.sender = sender
        self.channel = channel
        self.time = time

    def __str__(self):
        time_str = self.time.strftime("%Y-%m-%d %I:%M:%S %p")
        return "[{0}] <{1}> {2}: {3}".format(time_str, self.channel, self.sender, self.message)
