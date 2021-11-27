from utils.utils import Config, EmailWrapper, FileWrapper, LoggerWrapper
import utils.utils
from sqlalchemy import create_engine, text, exc
import sys
import pandas as pd
import requests
import time
import json
from subprocess import call

from unittest.mock import MagicMock
import os

ARTIST_RESULT_FILE = "/data/script_counters/artist_result.txt"
ARTIST_ID_FILE = "/data/script_counters/artist_id.txt"
MISSING_SONG_ATTRIBUTES_FILE = "/data/script_counters/missing_song_attributes.txt"
TWITTER_USER_QUEUE_FILE = "/data/script_counters/twitter_user_queue.txt"
SPOTIFY_MISSING_TWITTER_FILE = "/data/script_data/spotify_missing_twitter_file.txt"
LOG_PATH = '/data/script_logs/'
DATA_PATH = '/data/script_data/'

ARTIST_RESULT_CSV = "/code/prescraped/artist_result.csv"
ARTIST_RESULT_CSV = "prescraped/artist_result.csv"

FOLLOWER_ITER_CAP = 5

engine = None
logger = LoggerWrapper()
# logger = MagicMock()
config = Config()

headers = {"Authorization": "Bearer {:}".format(config.TWITTER_BEARER)}
# headers = {"Authorization": "Bearer {:}".format('')}
spotify_to_twitter = {}

#####################
# SPOTIFY ENDPOINTS #
#####################
# Retrieve and return a twitter username given a spotify ID
def extract_twitter_id(spotify_id):
    r = requests.get('https://open.spotify.com/artist/{:}'.format(spotify_id))

    if r.status_code != 200:
        logger.twitter_warn("Unable to perform HTTP request for ID: {:}".format(spotify_id))
        return -1

    # {"name":"TWITTER","url":"https://twitter.com/justinbieber"}
    try:
        twitter_id = r.text.split('{"name":"TWITTER","url":"https://twitter.com/')[1].split('"')[0].split('?')[0]
    except IndexError:
        logger.twitter_warn("User has not connected their Spotify to Twitter")
        FileWrapper.appendToFile(SPOTIFY_MISSING_TWITTER_FILE, "{:}".format(spotify_id))
        return -1

    return twitter_id

#####################
# TWITTER ENDPOINTS #
#####################

# Parses a dictionary of data about a Twitter user and write to db
def parse_twitter_user_and_write(data_obj):
    twitter_id = int(data_obj.get('id'))
    twitter_username = data_obj.get('username')
    twitter_name = data_obj.get('name')
    bio = data_obj.get('description')
    verified = data_obj.get('verified')
    protected = data_obj.get('protected')
    public_metrics = data_obj['public_metrics']
    followers_count = public_metrics.get('followers_count')
    following_count = public_metrics.get('following_count')
    tweet_count = public_metrics.get('tweet_count')
    listed_count = public_metrics.get('listed_count')

    twitter_user_obj = [twitter_id, twitter_username, twitter_name, bio, verified, protected, followers_count, following_count, tweet_count, listed_count]
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                    INSERT INTO twitter_user(twitter_id, twitter_username, twitter_name, verified, protected, followers_count, following_count, tweet_count, listed_count)
                    VALUES(:twitter_id, :twitter_username, :twitter_name, :verified, :protected, :followers_count, :following_count, :tweet_count, :listed_count)
                    RETURNING twitter_id
                    """).params(
                        twitter_id=twitter_id, 
                        twitter_username=twitter_username, 
                        twitter_name=twitter_name, 
                        verified=verified, 
                        protected=protected, 
                        followers_count=followers_count, 
                        following_count=following_count, 
                        tweet_count=tweet_count, 
                        listed_count=listed_count))
    except exc.IntegrityError:
        logger.twitter_warn("There was a duplicate twitter user for {:} {:}".format(twitter_id, twitter_username))

    return twitter_user_obj


# Retrieve and return a twitter id and write to database for an artist
def extract_base_twitter_info(twitter_username, spotify_id):
    # 300 calls per 15 minutes
    twitter_id_request_string = 'https://api.twitter.com/2/users/by/username/{:}?user.fields=id,name,verified,description,protected,public_metrics,location'
    user_id_r = requests.get(twitter_id_request_string.format(twitter_username), headers=headers)
    
    if user_id_r.status_code != 200:
        logger.twitter_warn("Unable to perform HTTP request for ID: {:}".format(twitter_username))
        return user_id_r.status_code
    
    json_data = json.loads(user_id_r.text)
    if "errors" in json_data:
        logger.twitter_warn("Error twitter response for user_id query: {:}".format(twitter_username))
        return -1

    data_obj = json_data['data']
    parse_twitter_user_and_write(data_obj)
    twitter_id = int(data_obj.get('id'))
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO artist(twitter_id, spotify_id)
                VALUES(:twitter_id, :spotify_id)
                RETURNING twitter_id
                """).params(
                    twitter_id=twitter_id,
                    spotify_id=spotify_id))
    except exc.IntegrityError:
        logger.twitter_warn("There was a duplicate artist for twitter {:} and spotify {:}".format(twitter_id, spotify_id))

    return twitter_id

# Retrieve and write a following list to database for an artist
def extract_twitter_following_info(twitter_id, next_token=""):
    # 15 calls per 15 minutes
    initial_followers_request_string = 'https://api.twitter.com/2/users/{:}/following?user.fields=id,name,username,verified,description,protected,public_metrics&max_results=1000'
    subsequent_followers_request_string = 'https://api.twitter.com/2/users/{:}/following?user.fields=id,name,username,verified,description,protected,public_metrics&max_results=1000&pagination_token={:}'
    if next_token == "":
        followers_r = requests.get(initial_followers_request_string.format(twitter_id), headers=headers)
    else:
        followers_r = requests.get(subsequent_followers_request_string.format(twitter_id, next_token), headers=headers)
        
    if followers_r.status_code != 200:
        logger.twitter_warn("Unable to perform HTTP request for ID: {:}".format(twitter_id))
        return followers_r.status_code, None
    
    if "errors" in followers_r:
        logger.twitter_warn("Error twitter response for followers query: {:} {:}".format(twitter_id, followers_r['errors']))
        return -1, None
    
    json_data = json.loads(followers_r.text)
    meta_obj = json_data.get('meta')
    next_token = json_data.get('next_token')

    data_obj = json_data.get('data')
    following_user_list = []
    if data_obj is None:
        return [], None
    for following_user in data_obj:
        following_user_data = parse_twitter_user_and_write(following_user)
        following_user_list.append(following_user_data)

        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    INSERT INTO following(follower_id, followed_id)
                    VALUES(:follower_id, :followed_id)
                    RETURNING follower_id
                    """).params(
                        follower_id=twitter_id,
                        followed_id=following_user_data[0]))
        except exc.IntegrityError:
            logger.twitter_warn("There was a duplicate following directed pair {:} to {:}".format(twitter_id, following_user_data[0]))
    
    return following_user_list, next_token

# timebox and extract twitter information
def extract_all(artist_result_offset=0, artist_following_offset=0):
    artist_result_df = pd.read_csv(ARTIST_RESULT_CSV, header=None, skiprows=artist_result_offset)
    artist_result_follower_df = pd.read_csv(ARTIST_RESULT_CSV, header=None, skiprows=artist_following_offset)

    artist_result_max = artist_result_df.index.stop
    artist_result_follower_max = artist_result_max

    u_count = 0
    f_count = 0
    f_ind_follower_iter = 0

    last_user_time = 0.0
    last_following_time = 0.0

    next_token = ""

    while True:
    # for k in range(1):
        # user queries

        # 300 per 15 minute, 20 per minute, 1 per 3 seconds
        for k in range(20):
            # print(u_count)
            curr_time = time.time()
            diff_delay = curr_time - last_user_time - 3
            if diff_delay < 0:
                time.sleep(-1*diff_delay + 0.1)

            u_ind = artist_result_offset + u_count
            if u_ind >= artist_result_max:
                break
            u_spotify_id = artist_result_df.iloc[u_ind, 0]
            u_spotify_name = artist_result_df.iloc[u_ind, 1]

            if u_count % 10 == 0:
                logger.twitter_debug("Parsing {:}th artist for HTML, {:}".format(u_count, u_spotify_name))

            # spotify_id -> twitter_username
            u_twitter_username = extract_twitter_id(u_spotify_id)
            if u_twitter_username == -1:
                u_count += 1
                continue

            # twitter_username, spotify_id -> twitter_id, @write(twitter_user)
            u_twitter_id = extract_base_twitter_info(u_twitter_username, u_spotify_id)
            last_user_time = time.time()
            if u_twitter_id == 429:
                logger.twitter_warn("Rate limit exceeded for users at {:}".format(u_count))
                continue
            if u_twitter_id == -1:
                u_count += 1
                continue
            
            # add to dictionary for easier follower queries
            spotify_to_twitter[u_spotify_id] = u_twitter_id
            u_count += 1
            # print(u_spotify_id, u_spotify_name, u_twitter_id)

        # follower_queries
        f_ind = artist_following_offset + f_count
        if f_ind >= artist_result_follower_max:
            break
        f_spotify_id = artist_result_follower_df.iloc[f_ind, 0]
        f_spotify_name = artist_result_follower_df.iloc[f_ind, 1]

        if f_count % 10 == 0:
            logger.twitter_debug("Parsing {:}th artist for followings, {:}".format(f_count, f_spotify_name))

        curr_time = time.time()
        diff_delay = curr_time - last_following_time - 60
        if diff_delay < 0:
            time.sleep(-1*diff_delay + 0.1)

        # 15 per 15 minute, 1 per minute, 1 per 60 seconds
        f_twitter_id = spotify_to_twitter.get(f_spotify_id)
        if f_twitter_id is None:
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT twitter_id
                        FROM artist
                        WHERE :spotify_id = spotify_id
                        """).params(
                            spotify_id=f_spotify_id)).first()
                    if (result is not None) and len(result) > 0:
                        f_twitter_id = result[0]
                        spotify_to_twitter[f_spotify_id] = f_twitter_id
            except exc.IntegrityError:
                logger.twitter_warn("There was an error retrieving twitter_id for spotify_id {:}", f_spotify_id)
        if f_twitter_id is None:
            f_count += 1
            f_ind_follower_iter = 0
            next_token = None
            logger.twitter_info("Can't get follower info for nonexistent twitter id {:} {:}".format(f_spotify_id, f_spotify_name))
            FileWrapper.appendToFile(SPOTIFY_MISSING_TWITTER_FILE, "{:},{:}".format(f_spotify_id, f_spotify_name))
            continue

        if next_token is None:
            next_token = ""
        # twitter_id, next_token='' -> following_user_list, next_token, @write(twitter_user, following)
        following_user_list, next_token = extract_twitter_following_info(f_twitter_id, next_token)
        last_following_time = time.time()
        if following_user_list == 429:
            logger.twitter_warn("Rate limit exceeded for followers at {:}".format(f_count))
        else:
            f_ind_follower_iter += 1
            # also accounts for other error case
            if next_token == None or next_token == "":
                f_count += 1
                f_ind_follower_iter = 0
            elif f_ind_follower_iter >= FOLLOWER_ITER_CAP: # practical cap of followings reached
                f_count += 1
                f_ind_follower_iter = 0
                next_token = None
            # print(f_spotify_id, f_spotify_name, f_twitter_id, following_user_list[:10])
        
        # logging/saving
        # ever ~5 mins
        if u_count % 100 == 0:
            logger.twitter_debug("Exporting counts for safety at count of {:} and {:}".format(u_count, f_count))
            FileWrapper.writeValToFile(ARTIST_RESULT_FILE, u_count+artist_result_offset)
            FileWrapper.writeValToFile(ARTIST_ID_FILE, f_count+artist_following_offset)

        # every ~30 mins
        if u_count % 600 == 0: # 600
            logger.twitter_debug("Exporting csvs for safety at count of {:} and {:}".format(u_count, f_count))
            rc = call("/code/db/export.sh")
            time.sleep(3)
            file_names = ["twitter_user.csv", "following.csv", "spotify_artist.csv", "artist.csv"]
            for f in file_names:
                topdir = FileWrapper.getMostRecentDir(DATA_PATH)
                curr_file_name = os.path.join(topdir, f)
                EmailWrapper.sendEmail("{:}: Sending logged csv".format(time.time()), subject="Twitifynd Alert {:}".format(f), attachment=curr_file_name)
        # end of while loop
    # end of func

if __name__ == "__main__":
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, execution_options={"isolation_level": "SERIALIZABLE"})
    if len(sys.argv) <= 2 or sys.argv[1] == "" or sys.argv[2] == "":
        logger.twitter_warn("Bad argument: {:} {:}".format(sys.argv[1] if len(sys.argv) > 1 else "missing", sys.argv[2] if len(sys.argv) > 2 else "missing"))
        sys.exit()
    # used for getting twitter name and id
    artist_twitter_offset = int(sys.argv[1])
    if artist_twitter_offset < 0:
        artist_twitter_offset = 0
    elif artist_twitter_offset > 20000:
        logger.twitter_info("Argument too large, skipping", artist_twitter_offset)
        sys.exit()

    # used for getting twitter follower relationships
    artist_following_offset = int(sys.argv[2])
    if artist_following_offset < 0:
        artist_following_offset = 0
    elif artist_following_offset > 20000:
        logger.twitter_info("Argument too large, skipping", artist_following_offset)
        sys.exit()
        
    logger.twitter_info("Beginning twitter parsing with {:} and {:}".format(artist_twitter_offset, artist_following_offset))
    extract_all(artist_twitter_offset, artist_following_offset)
