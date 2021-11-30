#!/bin/bash
sleep 4
echo "***Beginning setup of postgresql***"
/bin/bash db/create.sh

# If DB_PROCESS is 1 or 2, force an export or load and terminate
if [ $DB_PROCESS -eq 1 ]; then
    echo "Forcing an export"
    /bin/bash db/export.sh
    exit 0
elif [ $DB_PROCESS -eq 2 ]; then
    echo "Forcing a load"
    /bin/bash db/load_from_backup.sh
    exit 0
fi

# TODO: LOAD IN ANY PREVIOUS DATA AS APPLICABLE

sleep 1
echo "***Beginning analyzing artists***"

export PYTHONPATH="${PYTHONPATH}:/code/"

# Detect current values of ARTIST_RESULT_LINE, ARTIST_ID, MISSING_SONG_ATTRIBUTES, and TWITTER_USER_QUEUE
ARTIST_RESULT_FILE=/data/script_counters/artist_result.txt # The line of artist_result.csv that has been scraped for twitter_id
ARTIST_ID_FILE=/data/script_counters/artist_id.txt # The line of artist_result.csv that has been scraped for twitter followers
MISSING_SONG_ATTRIBUTES_FILE=/data/script_counters/missing_song_attributes.txt # The line of missing_song_attributes.csv that has been scraped for song attribute data
MISSING_SONG_FOLLOWERS_FILE=/data/script_counters/missing_song_followers.txt # The line of missing_song_followers.csv that has been scraped for follower data
TWITTER_USER_QUEUE_FILE=/data/script_counters/twitter_user_queue.txt # Deprecated
SECOND_TIER_USER_FILE=/data/script_counters/second_tier_user.txt # The line of missing_song_attributes.csv that has been scraped for twitter user data
SECOND_TIER_FOLLOWERS_FILE=/data/script_counters/second_tier_followers.txt # The line of missing_song_attributes.csv that has been scraped for twitter follower data

SPOTIFY_MISSING_TWITTER_FILE=/data/script_data/spotify_missing_twitter_file.csv
touch "${SPOTIFY_MISSING_TWITTER_FILE}"
chmod +w "${SPOTIFY_MISSING_TWITTER_FILE}"

SPOTIFY_MISSING_TWITTER_FILE_2=/data/script_data/spotify_missing_twitter_file_2.csv
touch "${SPOTIFY_MISSING_TWITTER_FILE_2}"
chmod +w "${SPOTIFY_MISSING_TWITTER_FILE_2}"

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

if [[ -f "$MISSING_SONG_FOLLOWERS_FILE" ]]; then
    MISSING_SONG_FOLLOWERS=$(cat "$MISSING_SONG_FOLLOWERS_FILE")
else
    MISSING_SONG_FOLLOWERS=-1
    touch "${MISSING_SONG_FOLLOWERS_FILE}"
    echo "-1" > ${MISSING_SONG_FOLLOWERS_FILE}
fi

if [[ -f "$TWITTER_USER_QUEUE_FILE" ]]; then
    TWITTER_USER_QUEUE=$(cat "$TWITTER_USER_QUEUE_FILE")
else
    TWITTER_USER_QUEUE=-1
    touch "${TWITTER_USER_QUEUE_FILE}"
    echo "-1" > ${TWITTER_USER_QUEUE_FILE}
fi

if [[ -f "$SECOND_TIER_USER_FILE" ]]; then
    SECOND_TIER_USERS=$(cat "$SECOND_TIER_USER_FILE")
else
    SECOND_TIER_USERS=-1
    touch "${SECOND_TIER_USER_FILE}"
    echo "-1" > ${SECOND_TIER_USER_FILE}
fi

if [[ -f "$SECOND_TIER_FOLLOWERS_FILE" ]]; then
    SECOND_TIER_FOLLOWERS=$(cat "$SECOND_TIER_FOLLOWERS_FILE")
else
    SECOND_TIER_FOLLOWERS=-1
    touch "${SECOND_TIER_FOLLOWERS_FILE}"
    echo "-1" > ${SECOND_TIER_FOLLOWERS_FILE}
fi

echo $ARTIST_RESULT_LINE $ARTIST_ID $MISSING_SONG_ATTRIBUTES $MISSING_SONG_FOLLOWERS $TWITTER_USER_QUEUE $SECOND_TIER_USERS $SECOND_TIER_FOLLOWERS

# If alert level is at least 2, email a startup message
if [ $ALERT_LEVEL -ge 2 ]; then
    python3 utils/utils.py $ARTIST_RESULT_LINE $ARTIST_ID $MISSING_SONG_ATTRIBUTES $TWITTER_USER_QUEUE
fi

# VVV IN PARALLEL VVV
# 1. Using the current value of ARTIST_RESULT_LINE, if it's less than the length of the file (~10,000):
#   a. Read the artist_result.csv into the database
EXIST_QUERY="SELECT COUNT(*) FROM spotify_artist;"
number_spotify_artists=$(psql -h db -p 5432 -U ${POSTGRES_USER} -c "$EXIST_QUERY" $POSTGRES_DB | tail -n 3 | head -n 1)

if [ $ARTIST_RESULT_LINE -eq -1 ] || [ $number_spotify_artists -eq 0 ]; then
    echo "Performing initial load"
    /bin/bash db/initial_load.sh
    echo "0" > ${ARTIST_RESULT_FILE}
else
    echo "Performing load from backup" # if tuple already exists, will not be overwritten, may throw warning
    /bin/bash db/load_from_backup.sh
fi
#   b. Note the null values, particularly twitter_id. Query the Spotify HTML page for their twitter_handles/ids (with waits)
#   c. Query Twitter API for follower/user data. Write/update to database.
#   d. Add followers/followings(?) as empty twitter_user stubs to database and via following relationship
#   e. Add followers/followings' IDs and handles to another file, relevant to TWITTER_USER_QUEUE.
#   f. Periodically update ARTIST_RESULT_LINE
# TODO: CALL PYTHON FILE WITH FOR QUERYING SPOTIFY WITH $ARTIST_RESULT_LINE
if [ $SKIP_ARTIST_RESULT -ne 1 ]; then
    echo "Beginning Twitter queries for artist_result"
    # uses artist_result.csv to convert spotify artists to twitter users and grab twitter information
    # also begins parsing for follower data
    if [ $USE_SECOND_TIER -eq 1 ]; then
        # use missing
        python3 twitter/parse_spotify_artists.py $USE_SECOND_TIER $SECOND_TIER_USERS $SECOND_TIER_FOLLOWERS
    else
        # use artist_result.csv
        python3 twitter/parse_spotify_artists.py $USE_SECOND_TIER $ARTIST_RESULT_LINE $ARTIST_ID        
    fi
else
    echo "Skipping Twitter queries for artist_result, parsing missing_artists.csv"
    # uses missing_artists.csv to fill in missing spotify artist info and 
    python3 spotify/artist_feature_data.py $MISSING_SONG_ATTRIBUTES $MISSING_SONG_FOLLOWERS
fi

#   If ARTIST_RESULT_LINE > length of the file (~10,000)
#   a. Query the database for null Twitter_ids, start at ARTIST_ID (maybe deprecate this variable)
#   b-d. Repeat b-d as above.
#   e. Periodically update ARTIST_ID

# 2. Using the current value of MISSING_SONG_ATTRIBUTES, if it's less than the length of missing_artists (most certainly, >1,000,000):
#   a. Starting at line MISSING_SONG_ATTRIBUTES in missing_artists.csv, query Spotify API for song attributes
#   b. Add artist to database in spotify_artist table
#   c. Periodically update MISSING_SONG_ATTRIBUTES
# TODO: @JUSTIN @ANDREW
# TODO: EVERY COUPLE HOURS OR SO IN THE SCRIPTS, EXPORT BY EXECUTING THE FOLLOWING:
# /bin/bash db/export.sh

# 3. OPTIONAL (although unlikely): use the names/handles from TWITTER_USER_QUEUE to do get other user data as desired

# ^^^ IN PARALLEL ^^^





# TODO: DEFINE A VIEW FOR THE ARTISTS THAT HAVE NON-NULL SPOTIFY AND TWITTER INFO

