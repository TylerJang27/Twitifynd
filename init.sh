#!/bin/bash

sleep 4
echo "***Beginning setup of postgresql***"
# TODO: PERFORM PERSISTENT LOGGING
/bin/bash db/create.sh

sleep 1
echo "***Beginning analyzing artists***"
# TODO: DETECT LAST INPUT OF ARTIST STREAM (Python)
# TODO: QUERY SPOTIFY FOR ARTIST INFO (Python)
# TODO: QUERY SPOTIFY FOR TWITTER HANDLE (Python)
# TODO: QUERY TWITTER FOR ARTIST FOLLOWER INFO (Python)
# TODO: ADD TWITTER USERS TO QUEUE (Python?)
# TODO: COMMIT TO DATABASE
# TODO: BACKUP/LOG/PERSIST DATABASE


ls /data
