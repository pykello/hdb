#!/usr/bin/env python

from hdb import client
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HDB stop script')
    parser.add_argument('port', action='store', type=int)
    
    args = parser.parse_args()
    port = args.port

    response = client.request(('localhost', port), {"code": "ServerList"})
    for server in response["server_list"]:
        print "Shutting down (%s, %d) ..." % (server[0], server[1])
        try:
            result = client.request(tuple(server), {"code": "Quit"})
            if result["code"] == "OK":
                print "OK."
            else:
                print "Failed."
        except:
            print "Failed."
