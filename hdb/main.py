import argparse
import sys
import graph
import request_server
from executor import Executor, ExecutorThread

def main(argv):
    port, node_count_max, rel_count_max = parse_args(argv)
    local_addr = ('localhost', port)
    distributed_graph = graph.DistributedGraph(node_count_max, rel_count_max,
                                               local_addr)
    executor = Executor(distributed_graph)
    server_thread = request_server.RequestServerThread(local_addr,
                                                       distributed_graph,
                                                       executor)
    executor_thread = ExecutorThread(executor)

    server_thread.start()
    executor_thread.start()

    # wait until request server is done
    server_thread.join()

    # server thread is done, so we can also stop the executor thread
    executor_thread.request_stop()
    executor_thread.join()

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
