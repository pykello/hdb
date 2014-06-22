#!/usr/bin/env python

from hdb import client
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HDB stat script')
    parser.add_argument('port', action='store', type=int)

    args = parser.parse_args()
    port = args.port

    response = client.request(('localhost', port), {"code": "ServerList"})
    for server in response["server_list"]:
        print server[1]
        result = client.request(tuple(server), {"code": "LocalStat"})
        if result["code"] == "OK":
            node_count = result["node_count"]
            node_count_max = result["node_count_max"]
            node_count_usage = (node_count * 100) / max(node_count_max, 1)
            
            rel_count = result["rel_count"]
            rel_count_max = result["rel_count_max"]
            rel_count_usage = (rel_count * 100) / max(rel_count_max, 1)

            print "Nodes: %d (%d%%)" % (node_count, node_count_usage, )
            print "Relationships: %d (%d%%)" % (rel_count, rel_count_usage, )
            print "Max Degree: %d" % (result["max_degree"], )
        else:
            print "Couldn't get statistics"
