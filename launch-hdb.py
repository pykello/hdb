#!/usr/bin/env python

import argparse
import os
import socket
import sys
import time

from hdb import client
from hdb import main
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
        s.bind((address, port))
        s.close()
        return True
    except socket.error, e:
        return False


def find_open_port(start_from):
    port = start_from
    while not is_port_open('localhost', port):
        port += 1

    return port


def get_bucket_map(ports):
    bucket_map = [['localhost', ports[i % len(ports)]] for i in range(4096)]
    return bucket_map


def send_bucket_map(hostname, port, bucket_map):
    msg = {"code": "BucketMapUpdate", "bucket_map": bucket_map}

    response = client.request((hostname, port), msg)
    if response["code"] != "OK":
        print "Error in sending bucket map to (localhost, %d)" % (port, )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HDB launch script')
    parser.add_argument('instance_count', action='store', type=int)
    parser.add_argument('node_count_max', action='store', type=int)
    parser.add_argument('rel_count_max', action='store', type=int)
    
    args = parser.parse_args()
    instance_count = args.instance_count
    node_count_max = args.node_count_max
    rel_count_max = args.rel_count_max

    port = 5430
    ports = []
    for i in range(instance_count):
        port = find_open_port(port)
        pid = os.fork()
        if pid == 0:
            daemon = HDBDaemon(stderr='/tmp/hdb.err', stdout='/tmp/hdb.out')
            daemon.set_args(['main.py', str(port), str(node_count_max),
                             str(rel_count_max)])
            daemon.start()
        else:
            sys.stdout.write("%d\n" % (port,))
            sys.stdout.flush()
            ports.append(port)
            port += 1

    time.sleep(1)

    bucket_map = get_bucket_map(ports)
    for port in ports:
        send_bucket_map('localhost', port, bucket_map)

    sys.exit(0)
