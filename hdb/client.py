import socket
import json

def request(server_addr, msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_addr)
    s.send(json.dumps(msg) + "$$$")
    response = read_response(s)
    response = json.loads(response)
    s.close()

    return response


def read_response(connection):
    response = ""
    while True:
        chunck = connection.recv(1024)
        response += chunck
        if not chunck:
            break
    return response


def get_bucket_map(server):
    bucket_map_request = {"code": "BucketMapGet"}
    bucket_map_response = request(server, bucket_map_request)
    bucket_map = bucket_map_response["bucket_map"]

    return bucket_map


def locate_node(node_id, bucket_map):
    bucketId = node_id % len(bucket_map)
    server = bucket_map[bucketId]
    return tuple(server)

