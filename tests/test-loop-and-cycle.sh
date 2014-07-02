#!/bin/sh

hdb_port_string=`./launch-hdb.py 2 10 100`
read -a ports <<< $hdb_port_string

echo "Loading ..."
./load-hdb.py ${ports[0]} < ./data/loop-and-cycle.1

echo "Querying ..."
./query-hdb.py ${ports[0]} <<< "=1 * *"
./query-hdb.py ${ports[0]} <<< "=2 * *"
./query-hdb.py ${ports[0]} <<< "=3 * *"
./query-hdb.py ${ports[0]} <<< "=1 * * * *"
./query-hdb.py ${ports[0]} <<< "=2 * * * *"
./query-hdb.py ${ports[0]} <<< "=3 * * * *"
./query-hdb.py ${ports[0]} <<< "=1 * * * * * *"
./query-hdb.py ${ports[0]} <<< "=1 * * * * * =1"
./query-hdb.py ${ports[0]} <<< "=1 * * * * * =2"
./query-hdb.py ${ports[0]} <<< "=1 * * * * * =3"


./stop-hdb.py ${ports[0]}
