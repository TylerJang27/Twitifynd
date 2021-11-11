#!/bin/bash

sleep 4
echo "***Beginning setup of postgresql***"
/bin/bash db/create.sh

sleep 1
echo "***Beginning analyzing artists***"

# Detect current values of ARTIST_RESULT_LINE, ARTIST_ID, MISSING_SONG_ATTRIBUTES, and TWITTER_USER_QUEUE
ARTIST_RESULT_FILE=/data/script_counters/artist_result.txt
ARTIST_ID_FILE=/data/script_counters/artist_id.txt
MISSING_SONG_ATTRIBUTES_FILE=/data/script_counters/missing_song_attributes.txt
TWITTER_USER_QUEUE_FILE=/data/script_counters/twitter_user_queue.txt

if [[ -f "$ARTIST_RESULT_FILE" ]]; then
    ARTIST_RESULT_LINE=$(cat "$ARTIST_RESULT_FILE")
else
    ARTIST_RESULT_LINE=-1
    touch "${ARTIST_RESULT_FILE}"
    echo "-1" > ${ARTIST_RESULT_FILE}
fi

if [[ -f "$ARTIST_ID_FILE" ]]; then
    ARTIST_ID=$(cat "$ARTIST_ID_FILE")
else
    ARTIST_ID=-1
    touch "${ARTIST_ID_FILE}"
    echo "-1" > ${ARTIST_ID_FILE}
fi

if [[ -f "$MISSING_SONG_ATTRIBUTES_FILE" ]]; then
    MISSING_SONG_ATTRIBUTES=$(cat "$MISSING_SONG_ATTRIBUTES_FILE")
else
    MISSING_SONG_ATTRIBUTES=-1
    touch "${MISSING_SONG_ATTRIBUTES_FILE}"
    echo "-1" > ${MISSING_SONG_ATTRIBUTES_FILE}
fi

if [[ -f "$TWITTER_USER_QUEUE_FILE" ]]; then
    TWITTER_USER_QUEUE=$(cat "$TWITTER_USER_QUEUE_FILE")
else
    TWITTER_USER_QUEUE=-1
    touch "${TWITTER_USER_QUEUE_FILE}"
    echo "-1" > ${TWITTER_USER_QUEUE_FILE}
fi

echo $ARTIST_RESULT_LINE $ARTIST_ID $MISSING_SONG_ATTRIBUTES $TWITTER_USER_QUEUE

# If alert level is at least 2, email a startup message
if [ $ALERT_LEVEL -ge 2 ]; then
    python3 utils/utils.py $ARTIST_RESULT_LINE $ARTIST_ID $MISSING_SONG_ATTRIBUTES $TWITTER_USER_QUEUE
fi

# VVV IN PARALLEL VVV
# 1. Using the current value of ARTIST_RESULT_LINE, if it's less than the length of the file (~10,000):
#   a. Read the artist_result.csv into the database
#   b. Note the null values, particularly twitter_id. Query the Spotify HTML page for their twitter_handles/ids (with waits)
#   c. Query Twitter API for follower/user data. Write/update to database.
#   d. Add followers/followings(?) as empty twitter_user stubs to database and via following relationship
#   e. Add followers/followings' IDs and handles to another file, relevant to TWITTER_USER_QUEUE.
#   f. Periodically update ARTIST_RESULT_LINE

#   If ARTIST_RESULT_LINE > length of the file (~10,000)
#   a. Query the database for null Twitter_ids, start at ARTIST_ID
#   b-d. Repeat b-d as above.
#   e. Periodically update ARTIST_ID

# 2. Using the current value of MISSING_SONG_ATTRIBUTES, if it's less than the length of missing_artists (most certainly, >1,000,000):
#   a. Starting at line MISSING_SONG_ATTRIBUTES in missing_artists.csv, query Spotify API for song attributes
#   b. Add artist to database
#   c. Periodically update MISSING_SONG_ATTRIBUTES

# 3. OPTIONAL (although unlikely): use the names/handles from TWITTER_USER_QUEUE to do get other user data as desired

# ^^^ IN PARALLEL ^^^


# TODO: ON A CRONJOB EVERY (1?) HOURS, OUTPUT ALL THE TABLES TO CSVS AND EMAIL THEM

# TODO: DEFINE A VIEW FOR THE ARTISTS THAT HAVE NON-NULL SPOTIFY AND TWITTER INFO

