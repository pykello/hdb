import SocketServer
import threading
import requests
import socket
import json

class RequestServerThread(threading.Thread):
    def __init__(self, local_addr, distributed_graph, executor):
        super(RequestServerThread, self).__init__()
        self.distributed_graph = distributed_graph
        self.local_addr = local_addr
        self.executor = executor

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(self.local_addr)
        server_socket.listen(1)

        done = False
        while not done:
            connection, address = server_socket.accept()
            request_string = self.read_request(connection)
            if self.is_quit_request(request_string):
                connection.send('{"code":"OK"}')
                connection.close()
                done = True
            else:
                request = requests.parse_request(request_string)
                response = request.process(self.distributed_graph, self.executor)
                connection.send(response)
                connection.close()

        server_socket.close()

    def read_request(self, connection):
        request = ""
        run_count = 0
        while run_count < 3:
            c = connection.recv(1)
            if c == '$':
                run_count += 1
            else:
                request += '$' * run_count
                request += c
                run_count = 0
        return request

    def is_quit_request(self, request_string):
        try:
            code = json.loads(request_string)["code"]
            if code == "Quit":
                return True
            else:
                return False
        except:
            return False
