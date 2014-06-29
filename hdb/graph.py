import client

class DistributedGraph:
    def __init__(self, node_count_max, rel_count_max, local_addr):
    	self.node_count_max = node_count_max
        self.rel_count_max = rel_count_max
        self.local_addr = local_addr
        self.local_graph = LocalGraph(node_count_max, rel_count_max)
        self.bucket_map = []

    def update_bucket_map(self, bucket_map):
        self.bucket_map = bucket_map

    def get_bucket_map(self):
        return self.bucket_map

    def locate_node(self, node_id):
        bucketId = node_id % len(self.bucket_map)
        server = self.bucket_map[bucketId]
        return tuple(server)

    def get_server_list(self):
        result = []
        for server in self.bucket_map:
            if server not in result:
                result.append(server)
        return result

    def add_relation(self, source_id, rel_type_id, target_id):
        source_id = int(source_id)
        rel_type_id = int(rel_type_id)
        target_id = int(target_id)
        server_addr = self.locate_node(source_id)

        if server_addr == self.local_addr:
            result = self.local_graph.add_relation(source_id, rel_type_id, target_id)
        else:
            msg = {"code": "RelationAdd",
                   "relation": [source_id, rel_type_id, target_id]}
            response = client.request(server_addr, msg)
            result = response["added"]

        return result


class LocalGraph:
    def __init__(self, node_count_max, rel_count_max):
        self.node_count_max = node_count_max
        self.rel_count_max = rel_count_max
        self.graph = {}
        self.node_count = 0
        self.rel_count = 0
        self.max_degree = 0

    def add_relation(self, source_id, rel_type_id, target_id):
        if self.rel_count == self.rel_count_max:
            return False

        if source_id not in self.graph:
            if self.node_count == self.node_count_max:
                return False

            self.graph[source_id] = set()
            self.node_count += 1


        if (rel_type_id, target_id) in self.graph[source_id]:
            return False

        self.graph[source_id].add((rel_type_id, target_id))
        self.rel_count += 1
        self.max_degree = max(self.max_degree, len(self.graph[source_id]))

        return True
