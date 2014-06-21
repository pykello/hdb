#!/usr/bin/env python

import os
import socket
import sys

import main
from daemon import Daemon

class HDBDaemon(Daemon):
    def run(self):
        main.main(self.args)

    def set_args(self, args):
        self.args = args


def is_port_open(address, port):
    s = socket.socket()
    try:
        s.connect((address, port))
        s.close()
        return False
    except socket.error, e:
        return True


def find_open_port(start_from):
    port = start_from
    while not is_port_open('localhost', port):
        port += 1

    return port


if __name__ == "__main__":
    instance_count = int(sys.argv[1])
    node_max = sys.argv[2]
    rel_max = sys.argv[3]

    port = 5430
    for i in range(instance_count):
        port = find_open_port(port)
        pid = os.fork()
        if pid == 0:
            daemon = HDBDaemon(stderr='/tmp/hdb.err', stdout='/tmp/hdb.out')
            daemon.set_args(['main.py', str(port), node_max, rel_max])
            daemon.start()
        else:
            print port
            port += 1

    sys.exit(0)
