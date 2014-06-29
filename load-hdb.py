#!/usr/bin/env python

from hdb import client
import argparse
import sys

BATCH_SIZE = 1000

def main():
    parser = argparse.ArgumentParser(description='HDB stop script')
    parser.add_argument('port', action='store', type=int)
    
    args = parser.parse_args()
    server = ('localhost', args.port)

    bucket_map = get_bucket_map(server)
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


def get_bucket_map(server):
    bucket_map_request = {"code": "BucketMapGet"}
    bucket_map_response = client.request(server, bucket_map_request)
    bucket_map = bucket_map_response["bucket_map"]

    return bucket_map


def enqueue_rel(queue, relation, bucket_map):
    source = int(relation[0])
    server = locate_node(source, bucket_map)
    if server not in queue:
        queue[server] = []
    queue[server].append(relation)


def locate_node(node_id, bucket_map):
    bucketId = node_id % len(bucket_map)
    server = bucket_map[bucketId]
    return tuple(server)


def flush_rel_queue(rel_queue, bucket_map):
    loaded = 0

    for server, rels in rel_queue.items():
        add_request = {"code": "RelationBatchAdd", "relations": rels}
        result = client.request(server, add_request)
        loaded += result["added"]

    return loaded

if __name__ == "__main__":
    main()
