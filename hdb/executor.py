import threading
import time

class ExecutorThread(threading.Thread):
    def __init__(self, executor):
        super(ExecutorThread, self).__init__()
        self.executor = executor
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            self.executor.process()

    def request_stop(self):
        self.stop_event.set()


class Executor:
    def __init__(self, distributed_graph):
        self.distributed_graph = distributed_graph

    def process(self):
        time.sleep(0.5)
