import threading
from datetime import datetime
from enum import Enum

class ThreadedService(threading.Thread):

    service_id = 1

    def __init__(self):
        self.connectionType = None
        self.stop_handler = None
        self.start_time = None
        self.end_time = None
        self.started = False
        self.id = ThreadedService.service_id
        ThreadedService.service_id += 1
        threading.Thread.__init__(self)

    def start(self):
        self.start_time = datetime.now()
        self.started = True
        self.autoreconnect = True
        super(ThreadedService, self).start()

    def run(self):
        raise NotImplementedError()

    def stop(self):
        self.finished()
        raise NotImplementedError()

    #Functions for statistics
    def status(self):
        if self.started == False:
            return ThreadStatus.Ready
        if self.is_alive():
            return ThreadStatus.Running
        return ThreadStatus.Complete

    def uptime(self):
        if self.start_time is None:
            return None
        if self.end_time is None:
            return datetime.now() - self.start_time

        return self.end_time - self.start_time

    #Functions for callback on stopping
    def on_stop(self, function):
        self.stop_handler = function

    def finished(self):
        self.end_time = datetime.now()
        if self.stop_handler is not None:
            self.stop_handler(self)


class ThreadStatus(Enum):
    Ready = "Ready"
    Running = "Running"
    Complete = "Disconnected"
