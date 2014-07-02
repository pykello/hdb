hdb
===

hdb - a simple sharded in-memory graph database


Sharding
--------

HDB shards data based on nodes. All relations with the same source will be
located in the same node. Reasoning:
 
 * This was simple,
 * When traversing the graph we usually need to look at most relations of
   the node we are visiting,
 * In real-life scenario max-degree usually has a limit so having all relations
   of a single node in a single server usually doesn't cause a problem.

HDB's sharding algorithm is based on Couchbase. We have a fixed number of
buckets (default: 4096). Buckets are distributed evenly on servers. Fixed number
of buckets makes it easier to add or remove nodes, but it also puts a limitation
on max number of servers in a cluster. That is OK for now, because most clusters
have much less servers than 4096, and we can solve the scalibility problem by
using a better formula for nodeId to bucketId mapping.

bucketId to server mapping happens using a simple array. For simplicity, the
mapping array is communicated to servers using client scripts. Currently, only
the startup script will communicate the mapping to the servers. In future, we
can implement a rebalance script to update the mapping and add/remove servers
from the cluster.

nodeId to bucketId mapping happens using the following algorithm:

    bucketId = nodeId % bucketCount;


So in summary, to map a graph node to a server, we do:
   
    bucketId = nodeId % bucketCount;
    serverId = bucket2server[bucketId];

and each of the servers have the same copy of bucket2server.


Request Protocol
----------------

Each request to a server a json document followed by $$$.

Request type is specified in the "code" field of the json document. Valid values
for "code" field are:

 * BucketMapUpdate: to update bucket2server mapping of the cluster
 * BucketMapGet: to get the bucket2server mapping.
 * ServerList: to get list of servers registered in the cluster.
 * RelationAdd: to add a single relation to the cluster.
 * RelationBatchAdd: to add a batch of relations to the cluster.
 * LocalStat: to get statistics for local graph of a single server.
 * QueryExecute: to start execution of a server. Returns the task_key for the
   root task. This task_key can be used to later poll the status and result of
   the query.
 * TaskAssign: to assign a task which performs part of the execution. Each query
   execution can have many tasks. Returns the task_key.
 * TaskStatus: to get the status of a task, given the task_key.
 * TaskResult: to get the result of a task, given the task_key.

To see more details parameters and return fields for each of the requests, please
see hdb/requests.py


Execution Model
---------------

HDB is designed such that each request should return very quickly. So, it doesn't
return the result of the query in the same request. Instead, it returns a token
which can be used by the client application to poll the status of the query. When
the status request returns "Done", then client can poll for the result of the query
in a separate request.

Having each request return fast simplifies the server design. Now, we can respond
to all requests in the same thread.

Server has two components:

 * Request Server: which listens to the tcp port, and puts tasks in the task queue
   that is shared with execution server.
 * Execution Server: which fetches items from the shared task queue, processes them,
   and possibly creates new tasks. When a task is done, it's status and result is
   updated in two shared hash maps which the request server can use to answer
   TaskStatus and TaskResult requests.

Each query execution creates a tree of tasks. A task can be either a local task, or
a remote task. A local task is a task whose root graph node is in the local graph,
and a remote task is a task that needs to be executed in a different server. Each
remote task corresponds to a local task in some other server.


Tools
-----

 * ```./launch-hdb.py instance-count max-node-count max-rel-count```, which starts
   a local cluster, and prints the ports assigned to the servers.
 * ```./stop-hdb.py port```, which shuts-down a whole cluster,
 * ```./stat-hdb.py port```, which prints statistics for all nodes in the cluster,
 * ```./load-hdb.py port```, which is used to load data into the cluster. This script
   reads the relations from standard input. Each relation is specified in a separate
   line with the format: source_id rel_id target_id,
 * ```./query-hdb.py port```, which is used to query the cluster. This script reads
   the queries from each line of standard input.


Running Tests
-------------

To run tests, simply do ```./run-tests.sh```.


Software Requirements
---------------------

This software requires a Python 2.x installation. I haven't tested it with Python 3.x.


Query Language
--------------

The format of a query is as follows:
  ```<node filter> (<relationship filter> <node filter>)*```

Filters consist of one of the following:

  * ```=X``` - The node or relationship ID is exactly equal to X.
  * ```>X``` - The node or relationship ID is greater than X
  * ```<X``` - The node or relationship ID is less than X.
  * ```%X``` - The node or relationship ID is zero modulo X.
  * ```*```  - Matches any ID.

The query responds with all target nodes that match the query.

Examples:

  * ```=5``` Returns just "5" if a node with ID 5 exists, or nothing otherwise.

  * ```=5 =10 * =10 *``` Returns all nodes that are a two hops away from the "5" node, traversing only relationships of type "10".


**Note.** First node in query must be of the form ```=X```.


TODO
----

 * Currently loading happens in request server, which can be problematic. Move it
   to the execution server.
 * Currently we don't clean up resources after a query is finished. We should clean
   them up. Otherwise memory usage will grow.

