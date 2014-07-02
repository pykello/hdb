import client
import sys

class TaskStatus:
    READY = "Ready"
    RUNNING = "Running"
    DONE = "Done"
    FAILED = "Failed"


class LocalTask:
	def __init__(self, job_id, query, query_index, node, distributed_graph):
		self.job_id = job_id
		self.query = query
		self.query_index = query_index
		self.node = node
		self.distributed_graph = distributed_graph
		self.status = TaskStatus.READY
		self.result = set()
		self.pending_dependencies = []

	def __str__(self):
		return self.get_key()

	def process(self):
		new_tasks = []

		if self.status == TaskStatus.READY:
			if self.query_index == len(self.query) - 1:
				self.pending_dependencies = []
				self.result.add(self.node)
				self.status = TaskStatus.DONE
			else:
				new_tasks = self.get_dependencies()
				self.pending_dependencies = new_tasks
				self.status = TaskStatus.RUNNING
		else:
			self.check_dependencies()

		sys.stdout.flush()

		return new_tasks

	def get_key(self):
		return get_task_key(self)

	def get_dependencies(self):
		distributed_graph = self.distributed_graph
		graph = distributed_graph.local_graph.graph

		if self.node not in graph or self.query_index > len(self.query) - 3:
			return []

		rel_pattern = self.query[self.query_index + 1]
		target_pattern = self.query[self.query_index + 2]

		dependencies = []
		for rel, target in graph[self.node]:
			if matches_pattern(rel, rel_pattern) and matches_pattern(target, target_pattern):
				if distributed_graph.is_node_local(target):
					task = LocalTask(self.job_id, self.query, self.query_index + 2,
									 target, distributed_graph)
				else:
					server = distributed_graph.locate_node(target)
					task = RemoteTask(self.job_id, self.query, self.query_index + 2,
									  target, server)
				dependencies.append(task)

		return dependencies


	def check_dependencies(self):
		all_done = True
		any_failed = False
		new_pending_dependencies = []

		for dependency in self.pending_dependencies:
			if dependency.status == TaskStatus.DONE:
				self.result.update(dependency.result)
			elif dependency.status == TaskStatus.FAILED:
				any_failed = True
			else:
				all_done = False
				new_pending_dependencies.append(dependency)

		self.pending_dependencies = new_pending_dependencies

		if all_done:
			self.status = TaskStatus.DONE
		elif any_failed:
			self.status = TaskStatus.FAILED
		else:
			self.status = TaskStatus.RUNNING


class RemoteTask:
	def __init__(self, job_id, query, query_index, node, server):
		self.job_id = job_id
		self.query = query
		self.query_index = query_index
		self.node = node
		self.server = server
		self.status = TaskStatus.READY
		self.result = set()
		self.remote_task_key = None

	def __str__(self):
		return self.get_key()

	def process(self):
		if self.status == TaskStatus.READY:
			if self.assign_remote_task():
				self.status = TaskStatus.RUNNING
			else:
				self.status = TaskStatus.FAILED
		elif self.status == TaskStatus.RUNNING:
			remote_task_status = self.get_remote_task_status()
			if remote_task_status == TaskStatus.DONE:
				self.result = self.get_remote_task_result()
				self.status = TaskStatus.DONE
			elif remote_task_status == TaskStatus.FAILED:
				self.status = TaskStatus.FAILED
			else:
				self.status = TaskStatus.RUNNING

		# remote tasks don't create local dependencies, so we return empty list.
		return []

	def get_key(self):
		return get_task_key(self)

	def assign_remote_task(self):
		request = {"code": "TaskAssign", "job_id": self.job_id, "query": self.query,
				   "query_index": self.query_index, "node": self.node}
		response = client.request(self.server, request)
		if response["code"] == "OK":
			self.remote_task_key = response["task_key"]
			return True
		else:
			return False

	def get_remote_task_status(self):
		request = {"code": "TaskStatus", "task_key": self.remote_task_key}
		response = client.request(self.server, request)
		if response["code"] == "OK":
			return response["status"]
		else:
			return TaskStatus.FAILED

	def get_remote_task_result(self):
		request = {"code": "TaskResult", "task_key": self.remote_task_key}
		response = client.request(self.server, request)
		if response["code"] == "OK":
			return response["result"]
		else:
			return []


def get_task_key(task):
	task_key = "%d-%d-%d" % (task.job_id, task.query_index, task.node)
	return task_key


def matches_pattern(n, pattern):
	operator, m = pattern

	if operator == '*':
		return True
	if operator == '=':
		return n == m
	elif operator == '>':
		return n > m
	elif operator == '<':
		return n < m
	elif operator == '%':
		return n % m == 0
	else:
		return False

