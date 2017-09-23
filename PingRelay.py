#!/usr/bin/python

import os
from pathlib import Path
import logging
import toml
from datetime import datetime
from threading import Thread
from App import App
from ControlServer import ControlServer


def main():
    dir = os.path.dirname(__file__)
    config = loadConfig(dir)
    initLogging(dir, config)

    #Run app on a new thread
    app = App(config)
    thread = Thread(target =app.run)
    thread.start()

    #Run control server on new thread
    server = ControlServer(app, config)
    server.start()


def initLogging(dir, config):
    time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if "log_level" in config:
        log_name = config["log_level"]
    else:
        log_name = "INFO"

    if "module_log_level" in config:
        module_log_level = getattr(logging, config["module_log_level"] , "WARNING")
    else:
        module_log_level = getattr(logging, "WARNING")

    log_path =  os.path.join(dir, 'logs/pingRelay-{0}.{1}.log'.format(time_str, log_name.lower()))
    log_level = getattr(logging, log_name, "INFO")

    logging.basicConfig(filename=log_path,level=module_log_level, format='%(asctime)s - %(levelname)s - [%(name)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s')

    global _log
    _log = logging.getLogger("PingRelay")
    _log.setLevel(log_level)
    _log.debug("Log starts here")

def loadConfig(dir):
        #Import config from the TOML file
        file_path = os.path.join(dir, 'Config.toml')
        config_file = Path(file_path).read_text()
        return toml.loads(config_file)


if __name__== "__main__":
    main()
