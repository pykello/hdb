import SocketServer
import threading
import requests
import socket

class RequestServerThread(threading.Thread):
    def __init__(self, port, distributed_graph):
        super(RequestServerThread, self).__init__()
        self.distributed_graph = distributed_graph
        self.port = port

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(1)

        done = False
        while not done:
            connection, address = server_socket.accept()
            request_string = self.read_request(connection)
            if request_string == "quit":
                connection.close()
                done = True
            else:
                request = requests.parse_request(request_string)
                response = request.process(self.distributed_graph)
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
