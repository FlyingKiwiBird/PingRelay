#!/usr/bin/python

from Listeners.JabberListener import JabberListener
from Listeners.SlackListener import SlackListener
from Listeners.ListenerType import ListenerType
from Resources.ControlServer import ControlServer

from pprint import pprint
from pathlib import Path
from datetime import datetime

import toml
import os
import zerorpc
import logging

def main():
    dir = os.path.dirname(__file__)

    #Import config from the TOML file
    file_path = os.path.join(dir, 'Config.toml')
    config_file = Path(file_path).read_text()
    config = toml.loads(config_file)

    initLogging(dir, config)

    startListeners(config['listeners'])

def initLogging(dir, config):
    time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if "log_level" in config:
        log_name = config["log_level"]
    else:
        log_name = "INFO"

    log_path =  os.path.join(dir, 'logs/pingRelay-{0}.{1}.log'.format(time_str, log_name.lower()))
    log_level = getattr(logging, log_name, "INFO")
    logging.getLogger("sleekxmpp").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.basicConfig(filename=log_path,level=log_level, format='%(asctime)s - %(levelname)s - [%(name)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s')


def startListeners(listeners):
    for l in listeners:
        try:
            listenType = ListenerType[l['type'].upper()]
            listener = None
            if(listenType == ListenerType.JABBER):
                listener = JabberListener(l)
            elif(listenType == ListenerType.SLACK):
                listener = SlackListener(l)
            listener.onMessage(message)
            listener.connect()
        except Exception as e:
            logger.error("Could not start listener: {0}".format(e))
            pass


def message(msg):
    print(msg)


if __name__== "__main__":
    main()
