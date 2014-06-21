import json


def parse_request(request_string):
    request = None

    try:
        request_dict = json.loads(request_string)
        code = request_dict["code"]
        if code == "BucketMapUpdate":
            request = BucketMapUpdateRequest(request_dict)
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
