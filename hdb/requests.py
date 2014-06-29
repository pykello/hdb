import json


def parse_request(request_string):
    request = None

    try:
        request_dict = json.loads(request_string)
        code = request_dict["code"]
        if code == "BucketMapUpdate":
            request = BucketMapUpdateRequest(request_dict)
        elif code == "BucketMapGet":
            request = BucketMapGetRequest()
        elif code == "ServerList":
            request = ServerListRequest()
        elif code == "RelationAdd":
            request = RelationAddRequest(request_dict)
        elif code == "RelationBatchAdd":
            request = RelationBatchAddRequest(request_dict)
        elif code == "LocalStat":
            request = LocalStatRequest()
        else:
            request = InvalidRequest()
    except:
        request = InvalidRequest()

    return request


class InvalidRequest:
    def process(self, distributed_graph):
        response = {"code": "InvalidRequest"}
        return json.dumps(response)


class BucketMapUpdateRequest:
    def __init__(self, request):
        self.bucket_map = request["bucket_map"]

    def process(self, distributed_graph):
        distributed_graph.update_bucket_map(self.bucket_map)
        response = {"code": "OK"}
        return json.dumps(response)


class BucketMapGetRequest:
    def process(self, distributed_graph):
        response = {"code": "OK", "bucket_map": distributed_graph.get_bucket_map()}
        return json.dumps(response)


class ServerListRequest:
    def process(self, distributed_graph):
        server_list = distributed_graph.get_server_list()
        response = {"code": "OK", "server_list": server_list}
        return json.dumps(response)


class RelationAddRequest:
    def __init__(self, request):
        self.relation = request["relation"]

    def process(self, distributed_graph):
        result = distributed_graph.add_relation(*self.relation)
        response = {"code": "OK", "added": result}
        return json.dumps(response)


class RelationBatchAddRequest:
    def __init__(self, request):
        self.relations = request["relations"]

    def process(self, distributed_graph):
        result = 0
        for rel in self.relations:
            if distributed_graph.add_relation(*rel):
                result += 1
        response = {"code": "OK", "added": result}
        return json.dumps(response)


class LocalStatRequest:
    def process(self, distributed_graph):
        local_graph = distributed_graph.local_graph
        response = {
                        "code": "OK",
                        "node_count": local_graph.node_count,
                        "rel_count": local_graph.rel_count,
                        "max_degree": local_graph.max_degree,
                        "node_count_max": local_graph.node_count_max,
                        "rel_count_max": local_graph.rel_count_max,
                    }
        return json.dumps(response)
