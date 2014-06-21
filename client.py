import socket
import json

def request(hostname, port, msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.send(json.dumps(msg) + "$$$")
    response = json.loads(s.recv(1024))
    s.close()

    return response
