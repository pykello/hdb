import argparse
import sys
import graph
import request_server


def main(argv):
    port, node_count_max, rel_count_max = parse_args(argv)
    local_addr = ('localhost', port)
    distributed_graph = graph.DistributedGraph(node_count_max, rel_count_max,
                                               local_addr)
    server_thread = request_server.RequestServerThread(local_addr,
                                                       distributed_graph)

    server_thread.start()
    server_thread.join()
    sys.exit(0)


def parse_args(argv):
    parser = argparse.ArgumentParser(description='HDB - distributed graph database')
    parser.add_argument('port', action='store', type=int)
    parser.add_argument('node_count_max', action='store', type=int)
    parser.add_argument('rel_count_max', action='store', type=int)

    args = parser.parse_args(argv[1:])
    
    return args.port, args.node_count_max, args.rel_count_max


if __name__ == "__main__":
    main(sys.argv)
