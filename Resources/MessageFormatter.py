import re

import logging
_log = logging.getLogger("PingRelay")

class MessageFormatter():
    def __init__(self, message_format, alert_user="@everyone", time_format = "%Y-%m-%d %I:%M:%S %p"):
        self.format = message_format
        self.time_format = time_format
        self.alert_user = alert_user

    def format_message(self, message):
        regex = re.compile(r"%{(\w+)}")
        self.message = message
        result = regex.sub(self.fill_placeholder, self.format)
        _log.debug("Formatted with {0} resulted in {1}".format(self.format, result))
        return result

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
        if(placeholder == "alerts"):
            if self.message.has_alert:
                return self.alert_user + ": this message matched alert(s): " + self.message.get_alert_str() + "\n"
            else:
                return ""
        if(placeholder == "time"):
            return self.message.time.strftime(self.time_format)
        return match.group()
