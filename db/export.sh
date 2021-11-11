#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

curr_time=$(date +"%Y-%m-%d_%T")
new_dir="/data/script_data/log_${curr_time}"
mkdir "${new_dir}"

# Configure database
dbname=$POSTGRES_DB
EXPORT_QUERY="SELECT db_to_csv('${new_dir}');"

if [[ -n `psql -h db -p 5432 -U ${POSTGRES_USER} -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    echo -e "\tDatabase $dbname exists"
    psql -h db -p 5432 -U ${POSTGRES_USER} -c "$EXPORT_QUERY" $dbname # TODO: DEBUG, REPLACE WITH CLIENT-SIDE COPY RATHER THAN SERVER-SIDE
else
    createdb $dbname
    echo "Database does not exist!"
    exit 1
fi
