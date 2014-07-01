import threading
import time
import random
from Queue import Queue, Empty

class JobStatus:
    READY = "Ready"
    RUNNING = "Running"
    DONE = "Done"
    FAILED = "Failed"

class ExecutionQueueItem:
    JOB = 1
    LOCAL_TASK = 2
    REMOTE_TASK = 3

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

        # we start id sequence from a random number, so chance of concurrent
        # running job id collision between different servers is low. We could
        # use a better scheme here, but this is simple and should work for
        # our purposes.
        self.id_seq = SyncSeq(random.randint(0, 10**9))

        self.job_status = SyncDict()
        self.job_result = SyncDict()

        self.queue = Queue()

    def process(self):
        try:
            code, obj = self.queue.get_nowait()
            if code == ExecutionQueueItem.JOB:
                self.process_job(obj)
        except Empty:
            time.sleep(1.5)

    def start_job(self, query):
        job_id = self.id_seq.next()
        root_task = None # this will be actually created later when processing
        job = (job_id, query, root_task)

        self.job_status.set(job_id, JobStatus.READY)
        self.job_result.set(job_id, None)
        self.queue.put((ExecutionQueueItem.JOB, job))

        return job_id

    def process_job(self, job):
        job_id, query, root_task = job

        self.job_result.set(job_id, [])
        self.job_status.set(job_id, JobStatus.DONE)

    def get_job_status(self, job_id):
        return self.job_status.get(job_id)

    def get_job_result(self, job_id):
        return self.job_result.get(job_id)


class SyncDict:
    def __init__(self):
        self.lock = threading.Lock()
        self.dict = dict()

    def get(self, key):
        result = None

        self.lock.acquire()
        if key in self.dict:
            result = self.dict[key]
        self.lock.release()

        return result

    def set(self, key, value):
        self.lock.acquire()
        self.dict[key] = value
        self.lock.release()


class SyncSeq:
    def __init__(self, start):
        self.lock = threading.Lock()
        self.seq = start

    def next(self):
        self.lock.acquire()
        result = self.seq
        self.seq += 1
        self.lock.release()

        return result
