#!/usr/bin/env python

from hdb import client
import argparse
import os
import sys
import time

STATUS_CHECK_INTERVAL = 0.5
MAX_CHECK_COUNT = 8

def main():
    parser = argparse.ArgumentParser(description='HDB stop script')
    parser.add_argument('port', action='store', type=int)
    
    args = parser.parse_args()
    server = ('localhost', args.port)
    bucket_map = client.get_bucket_map(server)

    for line in sys.stdin:
        query = parse_query(line)
        if len(query) == 0:
            print "empty query"
            continue
        if query[0][0] != '=':
            print "query should start with a specific node"
            continue

        query_server = client.locate_node(query[0][1], bucket_map)
        query_result = execute_query(query, query_server)
        print query_result


def parse_query(line):
    result = []
    for token in line.split():
        if token[0] in ('=', '<', '>', '%'):
            result.append((token[0], int(token[1:])))
        elif token == '*':
            result.append(('*', 0))
        else:
            # simply ignore invalid tokens for now
            pass
    return result


def execute_query(query, server):
    execute_request = {"code": "QueryExecute", "query": query}
    response = client.request(server, execute_request)
    if response["code"] != "OK":
        return response

    job_id = response["job_id"]

    # check status of query until it finishes or fails
    done = False
    failed = False
    timed_out = False
    check_count = 0
    while not done and not failed and not timed_out:
        status_request = {"code": "QueryStatus", "job_id": job_id}
        response = client.request(server, status_request)
        check_count += 1
        if response["code"] != "OK" or response["status"] == "Failed":
            failed = True
        elif response["status"] == "DONE":
            done = True
        elif check_count == MAX_CHECK_COUNT:
            timed_out = True
        else:
            time.sleep(STATUS_CHECK_INTERVAL)

    if failed:
        return response

    if timed_out:
        return {"code": "TIMEDOUT"}

    # if not failed, the query succeeded and we can fetch the result
    result_request = {"code": "QueryResult", "job_id": job_id}
    response = client.request(server, result_request)
    return response


if __name__ == "__main__":
    main()
