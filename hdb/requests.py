import json

def parse_request(request_string):
    request_map = {
        "BucketMapUpdate": BucketMapUpdateRequest,
        "BucketMapGet": BucketMapGetRequest,
        "ServerList": ServerListRequest,
        "RelationAdd": RelationAddRequest,
        "RelationBatchAdd": RelationBatchAddRequest,
        "LocalStat": LocalStatRequest,
        "QueryExecute": QueryExecuteRequest,
        "QueryStatus": QueryStatusRequest,
        "QueryResult": QueryResultRequest,
    }

    request = None

    try:
        request_dict = json.loads(request_string)
        code = request_dict["code"]
        if code in request_map:
            request = request_map[code](request_dict)
        else:
            request = InvalidRequest()
    except:
        request = InvalidRequest()

    return request


class BaseRequest:
    def __init__(self, *args, **kwargs):
        pass


class InvalidRequest(BaseRequest):
    def process(self, distributed_graph, executor):
        response = {"code": "InvalidRequest"}
        return json.dumps(response)


class BucketMapUpdateRequest(BaseRequest):
    def __init__(self, request):
        self.bucket_map = request["bucket_map"]

    def process(self, distributed_graph, executor):
        distributed_graph.update_bucket_map(self.bucket_map)
        response = {"code": "OK"}
        return json.dumps(response)


class BucketMapGetRequest(BaseRequest):
    def process(self, distributed_graph, executor):
        response = {"code": "OK", "bucket_map": distributed_graph.get_bucket_map()}
        return json.dumps(response)


class ServerListRequest(BaseRequest):
    def process(self, distributed_graph, executor):
        server_list = distributed_graph.get_server_list()
        response = {"code": "OK", "server_list": server_list}
        return json.dumps(response)


class RelationAddRequest(BaseRequest):
    def __init__(self, request):
        self.relation = request["relation"]

    def process(self, distributed_graph, executor):
        result = distributed_graph.add_relation(*self.relation)
        response = {"code": "OK", "added": result}
        return json.dumps(response)


class RelationBatchAddRequest(BaseRequest):
    def __init__(self, request):
        self.relations = request["relations"]

    def process(self, distributed_graph, executor):
        result = 0
        for rel in self.relations:
            if distributed_graph.add_relation(*rel):
                result += 1
        response = {"code": "OK", "added": result}
        return json.dumps(response)


class LocalStatRequest(BaseRequest):
    def process(self, distributed_graph, executor):
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


class QueryExecuteRequest(BaseRequest):
    def process(self, distributed_graph, executor):
        response = {
            "code": "OK",
            "job_id": 1
        }

        return json.dumps(response)


class QueryStatusRequest(BaseRequest):
    def __init__(self, request):
        self.job_id = request["job_id"]

    def process(self, distributed_graph, executor):
        response = {
            "code": "OK",
            "status": "Failed"
        }

        return json.dumps(response)


class QueryResultRequest(BaseRequest):
    def __init__(self, request):
        self.job_id = request["job_id"]

    def process(self, distributed_graph, executor):
        response = {
            "code": "OK",
            "result": []
        }

        return json.dumps(response)
