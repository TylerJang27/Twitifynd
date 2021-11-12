#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

curr_time=$(date +"%Y-%m-%d_%T")

dbname=$POSTGRES_DB

data_dir="/data/script_data"
latest=$(ls -Art ${data_dir} | tail -n 1)
emailed=0

TABLE_QUERY="SELECT (table_name) AS schema_table FROM information_schema.tables t INNER JOIN information_schema.schemata s ON s.schema_name = t.table_schema WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema') AND t.table_type NOT IN ('VIEW')"
if [[ -n `psql -h db -p 5432 -U ${POSTGRES_USER} -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    echo -e "\tDatabase $dbname exists"
    table_list=$(psql -h db -p 5432 -U ${POSTGRES_USER} -c "$TABLE_QUERY" $dbname)
    table_list=($table_list)
    for table in ${table_list[@]:2:${#table_list[2]}-4}; do
        file_path="$data_dir/$latest/$table"
        if [[ -f "$file_path.csv" ]]; then
            IMPORT_QUERY="\copy ${table} FROM '${file_path}.csv' WITH (FORMAT CSV);"
            echo "Importing ${table} from csv at ${file_path}.csv"
            psql -h db -p 5432 -U ${POSTGRES_USER} -c "$IMPORT_QUERY" $dbname
        else
            if [ $emailed -eq 0 ]; then
                python3 /code/utils/send_email.py "$curr_time:$file_path.csv Missing for load from backup!"
                emailed=1
            fi
        fi
    done
else
    echo "Database does not exist!"
    exit 1
fi
