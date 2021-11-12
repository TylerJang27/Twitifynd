#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

curr_time=$(date +"%Y-%m-%d_%T")
new_dir="/data/script_data/log_${curr_time}"
mkdir "${new_dir}"

dbname=$POSTGRES_DB

TABLE_QUERY="SELECT (table_name) AS schema_table FROM information_schema.tables t INNER JOIN information_schema.schemata s ON s.schema_name = t.table_schema WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema') AND t.table_type NOT IN ('VIEW')"
if [[ -n `psql -h db -p 5432 -U ${POSTGRES_USER} -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    echo -e "\tDatabase $dbname exists"
    table_list=$(psql -h db -p 5432 -U ${POSTGRES_USER} -c "$TABLE_QUERY" $dbname)
    table_list=($table_list)
    for table in ${table_list[@]:2:${#table_list[2]}-4}; do
        EXPORT_QUERY="\copy ${table} TO '${new_dir}/$table.csv' WITH (FORMAT CSV);"
        echo "Exporting ${table} to csv at ${new_dir}/$table.csv"
        table_list=$(psql -h db -p 5432 -U ${POSTGRES_USER} -c "$EXPORT_QUERY" $dbname)
    done
else
    echo "Database does not exist!"
    exit 1
fi
