import re
from random import *


def anonymize(message):
    message_text = message.message
    message_text = datestamp_randomizer(message_text)
    message.message = message_text

def datestamp_randomizer(text):
    regex = re.compile(r"(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}.)(\d+)")
    return regex.sub(sub_ms, text)

def sub_ms(match):
    length = len(match.group(2))
    rand_max = (10 ** length) - 1 # so 9, 99, 999, etc.
    rand = randint(0, rand_max)
    rand_str = ("{:0" + str(length) + "d}").format(rand)
    return match.group(1) + rand_str
