#!/usr/bin/env python

import os
import socket
import sys
import time

import main
import json
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


def get_bucket_map(ports):
    bucket_map = [['localhost', ports[i % len(ports)]] for i in range(4096)]
    return bucket_map


def send_bucket_map(hostname, port, bucket_map):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    msg = {"code": "BucketMapUpdate", "bucket_map": bucket_map}
    s.send(json.dumps(msg) + "$$$")

    response = json.loads(s.recv(1024))
    if response["code"] != "OK":
        print "Error in sending bucket map to (localhost, %d)" % (port, )

    s.close()


if __name__ == "__main__":
    instance_count = int(sys.argv[1])
    node_max = sys.argv[2]
    rel_max = sys.argv[3]

    port = 5430
    ports = []
    for i in range(instance_count):
        port = find_open_port(port)
        pid = os.fork()
        if pid == 0:
            daemon = HDBDaemon(stderr='/tmp/hdb.err', stdout='/tmp/hdb.out')
            daemon.set_args(['main.py', str(port), node_max, rel_max])
            daemon.start()
        else:
            print port
            ports.append(port)
            port += 1

    time.sleep(2)

    bucket_map = get_bucket_map(ports)
    for port in ports:
        send_bucket_map('localhost', port, bucket_map)

    sys.exit(0)
