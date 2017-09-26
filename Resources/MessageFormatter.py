import re

class MessageFormatter():
    def __init__(self, format, time_format = "%Y-%m-%d %I:%M:%S %p"):
        self.format = format
        self.time_format = time_format

    def format(self, message):
        regex = re.compile(r"%{(\w+)}")
        self.message = message
        return regex.sub(fill_placeholder, self.format)

    def fill_placeholder(self, match):
        placeholder = match.group(1).lower()
        if (placeholder == "server"):
            return self.message.server
        if (placeholder == "channel"):
            return self.message.channel
        if(placeholder == "from"):
            return self.message.sender
        if(placeholder == "message"):
            return self.message.message
        if(placeholder == "time"):
            return self.message.time.strftime(self.time_format)
