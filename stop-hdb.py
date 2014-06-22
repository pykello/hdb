#!/usr/bin/env python

import client
import sys

if __name__ == "__main__":
    port = int(sys.argv[1])

    response = client.request(('localhost', port), {"code": "ServerList"})
    for server in response["server_list"]:
        print "Shutting down (%s, %d) ..." % (server[0], server[1])
        try:
            result = client.request(server[0], server[1], {"code": "Quit"})
            if result["code"] == "OK":
                print "OK."
            else:
                print "Failed."
        except:
            print "Failed."
