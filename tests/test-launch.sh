#!/bin/sh

hdb_port_string=`./launch-hdb.py 2 10 100`
read -a ports <<< $hdb_port_string

./stop-hdb.py ${ports[0]}

