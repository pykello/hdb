import threading
import time
import random
from Queue import Queue, Empty
import sys
from task import TaskStatus, LocalTask, RemoteTask

class TaskStatus:
    READY = "Ready"
    RUNNING = "Running"
    DONE = "Done"
    FAILED = "Failed"


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

        self.task_status = SyncDict()
        self.task_result = SyncDict()

        self.task_queue = Queue()

    def process(self):
        try:
            # we shouldn't infinitely block here, because otherwise executor 
            # thread can become unstoppable. So, we use get_nowait() instead
            # of get.
            task = self.task_queue.get_nowait()

            new_tasks = task.process()
            for new_task in new_tasks:
                if self.task_status.get(new_task.get_key()) is not None:
                    new_task.status = TaskStatus.DONE
                    continue
                sys.stdout.flush()
                self.task_status.set(new_task.get_key(), new_task.status)
                self.task_result.set(new_task.get_key(), new_task.result)
                self.task_queue.put(new_task)

            self.task_status.set(task.get_key(), task.status)
            self.task_result.set(task.get_key(), task.result)
            if task.status not in (TaskStatus.DONE, TaskStatus.FAILED):
                self.task_queue.put(task)

        except Empty:
            # in case the queue is empty, we sleep for a bit to avoid 100% cpu
            # usage when there is nothing to do. Note that when a query comes
            # in, until it succeeds or fails, there will be at least one task
            # in task_queue and we won't sleep and will utilize the cpu as much
            # as possible.
            time.sleep(0.05)

    def start_job(self, query):
        job_id = self.id_seq.next()
        task_key = self.assign_task(job_id, query, 0, query[0][1])

        return task_key

    def assign_task(self, job_id, query, query_index, node):
        task = LocalTask(job_id, query, query_index, node, self.distributed_graph)

        if self.task_status.get(task.get_key()) is None:
            self.task_status.set(task.get_key(), task.status)
            self.task_result.set(task.get_key(), task.result)
            self.task_queue.put(task)

        return task.get_key()

    def get_task_status(self, task_key):
        status = self.task_status.get(task_key)
        return status

    def get_task_result(self, task_key):
        result = list(self.task_result.get(task_key))
        return result


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
