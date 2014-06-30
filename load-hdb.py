#!/usr/bin/env python

from hdb import client
import argparse
import os
import sys

BATCH_SIZE = 1000

def main():
    parser = argparse.ArgumentParser(description='HDB stop script')
    parser.add_argument('port', action='store', type=int)
    
    args = parser.parse_args()
    server = ('localhost', args.port)

    bucket_map = client.get_bucket_map(server)
    queued_rels = {}

    loaded = 0
    queue_length = 0
    for line in sys.stdin:
        relation = line.split()
        if len(relation) == 0:
            continue
        enqueue_rel(queued_rels, relation, bucket_map)
        if queue_length == BATCH_SIZE:
            loaded += flush_rel_queue(queued_rels, bucket_map)
            queue_length = 0
            queued_rels = {}

    loaded += flush_rel_queue(queued_rels, bucket_map) 

    print "Loaded %d" % (loaded, )


def enqueue_rel(queue, relation, bucket_map):
    source = int(relation[0])
    server = client.locate_node(source, bucket_map)
    if server not in queue:
        queue[server] = []
    queue[server].append(relation)


def flush_rel_queue(rel_queue, bucket_map):
    loaded = 0
    child_pids = []

    for server, rels in rel_queue.items():
        pid = os.fork()
        if pid == 0:
            add_request = {"code": "RelationBatchAdd", "relations": rels}
            result = client.request(server, add_request)
            sys.exit(0)
        else:
            child_pids.append(pid)
        loaded += len(rels)

    for pid in child_pids:
        os.waitpid(pid, 0)

    return loaded

if __name__ == "__main__":
    main()
