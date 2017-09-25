from enum import Enum

class ListenerType(Enum):
    JABBER = 1
    SLACK = 2
    DISCORD = 3
    MOCK = 999
