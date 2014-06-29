#!/bin/sh

hdb_port_string=`./launch-hdb.py 2 10 100`
read -a ports <<< $hdb_port_string

echo "Loading ..."
./load-hdb.py ${ports[0]} < ./data/graph.1

echo "Getting statistics ..."
./stat-hdb.py ${ports[0]}

./stop-hdb.py ${ports[0]}

