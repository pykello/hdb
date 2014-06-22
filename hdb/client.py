import socket
import json

def request(server_addr, msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_addr)
    s.send(json.dumps(msg) + "$$$")
    response = json.loads(read_response(s))
    s.close()

    return response


def read_response(connection):
    return connection.recv(1024)
