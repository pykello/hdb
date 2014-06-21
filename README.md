hdb
===

hdb - a simple sharded graph database


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

Each request to a server a json document followed by an empty line.

