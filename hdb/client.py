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

