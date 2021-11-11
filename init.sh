#!/bin/bash

sleep 4
echo "***Beginning setup of postgresql***"
/bin/bash db/create.sh

sleep 1
echo "***Beginning analyzing artists***"

# If alert level is at least 3, log a startup message
if [ $ALERT_LEVEL -ge 2 ]; then
    python3 utils/utils.py
fi


#       vvv ALL BELOW COULD BE CALLED HIERARCHICALLY IN PYTHON vvv
# TODO: DETECT LAST INPUT OF ARTIST STREAM (Python)
# TODO: QUERY SPOTIFY FOR ARTIST INFO (Python)          time boxed
# TODO: QUERY SPOTIFY FOR TWITTER HANDLE (Python)       time boxed
# TODO: QUERY TWITTER FOR ARTIST FOLLOWER INFO (Python) time boxed
# TODO: ADD relevant TWITTER USERS TO QUEUE (Python?)
# TODO: ADD/COMMIT TO DATABASE
# TODO: BACKUP/LOG/PERSIST DATABASE


