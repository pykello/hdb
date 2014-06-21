

class DistributedGraph:
    def __init__(self, node_count_max, rel_count_max):
    	self.node_count_max = node_count_max
        self.rel_count_max = rel_count_max
        self.bucket_map = []

    def update_bucket_map(self, bucket_map):
        self.bucket_map = bucket_map

    def locate_node(self, node_id):
        bucketId = node_id % len(self.bucket_map)
        server = self.bucket_map[bucketId]
        return server
