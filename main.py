#!/usr/bin/python

from Listeners.jabberListener import JabberListener
from Listeners.listenerType import ListenerType
from pprint import pprint
from pathlib import Path
import toml
import os

def main():
    #Import config from the TOML file
    dir = os.path.dirname(__file__)
    file_path = os.path.join(dir, 'Config.toml')
    config_file = Path(file_path).read_text()
    config = toml.loads(config_file)
    pprint(config)
    startListeners(config['listeners'])


def startListeners(listeners):
    for l in listeners:
        try:
            listenType = ListenerType[l['type'].upper()]
            listener = None
            if(listenType == ListenerType.JABBER):
                listener = JabberListener(l)
            listener.onMessage(message)
            listener.connect()
        except Exception as e:
            print(e)
            pass


def message(msg):
    pprint(msg)


if __name__== "__main__":
    main()
