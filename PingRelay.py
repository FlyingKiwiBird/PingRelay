#!/usr/bin/python

import os
import sys
from pathlib import Path
import logging
import toml
from datetime import datetime
from threading import Thread
from App import App
from ControlServer import ControlServer
from Reconnect import Reconnect


def main():
    dir = os.path.dirname(__file__)
    config = loadConfig(dir)
    initLogging(dir, config)

    #Run app on a new thread
    app = App(config)
    app.run()

    #Reconnects in case of error
    recon = Reconnect(app, config)
    recon.start()

    #Control server
    server = ControlServer(app, config)
    server.start()


def initLogging(dir, config):
    time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    log_name = config.get("log_level", "INFO")
    mod_log_level = config.get("module_log_level", "WARN")

    log_path =  os.path.join(dir, 'logs/pingRelay-{0}.{1}.log'.format(time_str, log_name.lower()))
    log_level = _toLogLevel(log_name)
    mod_level = _toLogLevel(mod_log_level)
    
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s')
    
    #File handler
    log_file_handler = logging.FileHandler(log_path)
    log_file_handler.setFormatter(log_format)

    #Stream handler
    log_stream_handler = logging.StreamHandler(sys.stdout)
    log_stream_handler.setFormatter(log_format)
    
    #Main log
    root = logging.getLogger()
    root.setLevel(mod_level)
    root.addHandler(log_file_handler)
    root.addHandler(log_stream_handler)
    log = logging.getLogger("PingRelay")
    log.setLevel(log_level)
    log.error("Log starting with level: '{}', module level: '{}'".format(log_name, mod_log_level))

def _toLogLevel(name):
    log_level = getattr(logging, name.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % name)
    else:
        return log_level

def loadConfig(dir):
        #Import config from the TOML file
        file_path = os.path.join(dir, 'Config.toml')
        config_file = Path(file_path).read_text()
        return toml.loads(config_file)


if __name__== "__main__":
    main()
