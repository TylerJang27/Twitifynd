#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

# Configure database
dbname=$POSTGRES_DB
if [[ -n `psql -h db -p 5432 -U ${POSTGRES_USER} -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    echo -e "\tDatabase $dbname already exists"
else
    createdb $dbname
    echo "Database created"
fi

# Configure table
echo "Beginning check for table existence in postgresql"

EXIST_QUERY="SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'artist');"
EXIST_RES=$(psql -h db -p 5432 -U ${POSTGRES_USER} -c "$EXIST_QUERY" $dbname)
EXIST_RES=${EXIST_RES/exists/""}
echo $EXIST_RES

if [[ "$EXIST_RES" == *"t"* ]]; then
    echo -e "\tTable exists."
elif [[ "$EXIST_RES" == *"f"* ]]; then
    echo "Table does not exist. Creating now"
    psql -h db -p 5432 -U $POSTGRES_USER -af create.sql $dbname
else
    echo "UNKNOWN ERROR."
    exit 1
fi

