#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

dbname=$POSTGRES_DB

LOAD_QUERY="\copy spotify_artist FROM '/code/prescraped/artist_result.csv' WITH (FORMAT CSV);"

if [[ -n `psql -h db -p 5432 -U ${POSTGRES_USER} -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    echo -e "\tDatabase $dbname exists"
    psql -h db -p 5432 -U ${POSTGRES_USER} -c "$LOAD_QUERY" $dbname
else
    echo "Database does not exist!"
    exit 1
fi
