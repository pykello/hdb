import sys
import graph
import request_server


DEFAULT_NODE_COUNT_MAX = 1000
DEFAULT_REL_COUNT_MAX = 10000


def main(argv):
    port, node_count_max, rel_count_max = parse_args(argv)
    distributed_graph = graph.DistributedGraph(node_count_max, rel_count_max)
    server_thread = request_server.RequestServerThread(port, distributed_graph)

    server_thread.start()
    server_thread.join()


def parse_args(argv):
    port = int(argv[1])

    try:
        node_count_max = int(argv[2])
        rel_count_max = int(argv[3])
    except:
        node_count_max = DEFAULT_REL_COUNT_MAX
        rel_count_max = DEFAULT_REL_COUNT_MAX

    return port, node_count_max, rel_count_max


if __name__ == "__main__":
    main(sys.argv)
