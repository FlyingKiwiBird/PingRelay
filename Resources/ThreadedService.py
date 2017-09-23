import threading
from datetime import datetime
from enum import Enum

class ThreadedService(threading.Thread):

        stop_handler = None
        start_time = None
        end_time = None
        started = False

        def __init__(self):
            threading.Thread.__init__(self)

        def start(self):
            self.start_time = datetime.now()
            self.started = True
            super(ThreadedService, self).start()

        def run(self):
            raise NotImplementedError()

        def stop(self):
            self.finished()
            raise NotImplementedError()

        #Functions for statistics
        def status(self):
            if started == False:
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
    Complete = "Complete"
