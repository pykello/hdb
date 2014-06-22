#!/usr/bin/env python

from hdb import client
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HDB stop script')
    parser.add_argument('port', action='store', type=int)
    
    args = parser.parse_args()
    server = ('localhost', args.port)

    loaded = 0
    for line in sys.stdin:
        relation = line.split()
        if len(relation) == 0:
            continue
        result = client.request(server, {"code": "RelationAdd", "relation": relation})
        if result["code"] != "OK":
            print "Failed to add %s" % (str(relation), )
        else:
            loaded += 1

    print "Loaded %d" % (loaded, )
