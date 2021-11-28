import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from utils.utils import Config, EmailWrapper, FileWrapper, LoggerWrapper
import utils.utils as utils
from sqlalchemy import create_engine, text, exc
import pandas as pd
import numpy as np
import time
import sys
from collections import defaultdict
import statistics
from subprocess import call

from unittest.mock import MagicMock
import os

from twitter.parse_spotify_artists import extract_twitter_id, parse_twitter_user_and_write, extract_base_twitter_info, extract_twitter_following_info

ARTIST_RESULT_FILE = utils.ARTIST_RESULT_FILE
ARTIST_ID_FILE = utils.ARTIST_ID_FILE
MISSING_SONG_ATTRIBUTES_FILE = utils.MISSING_SONG_ATTRIBUTES_FILE
MISSING_SONG_FOLLOWERS_FILE = utils.MISSING_SONG_FOLLOWERS_FILE
TWITTER_USER_QUEUE_FILE = utils.TWITTER_USER_QUEUE_FILE
SPOTIFY_MISSING_TWITTER_FILE = utils.SPOTIFY_MISSING_TWITTER_FILE
SPOTIFY_MISSING_TWITTER_FILE_2 = utils.SPOTIFY_MISSING_TWITTER_FILE_2
LOG_PATH = utils.LOG_PATH
DATA_PATH = utils.DATA_PATH
MISSING_ARTISTS_CSV = "/code/prescraped/missing_artists.csv"
'''
In order to run this script, first run:
    pip install python-dotenv
    cp template.env .env # edit it to contain the spotify_id and spotify_secret token
   
API Reference: https://developer.twitter.com/en/docs/api-reference-index
'''

# %% Environment setup
engine = None
logger = LoggerWrapper()
# logger = MagicMock()
config = Config()
spotify_to_twitter = {}
client_credentials_manager = SpotifyClientCredentials(config.SPOTIFY_ID, config.SPOTIFY_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#  get user's top artists
#   - current_user_top_artists(limit=20, offset=0, time_range='medium_term')
#  loop through top artists
#  get their top tracks
#  - artist_top_tracks(artist_id, country='US')
#  get audio features for each of that artists tracks
#  - audio_features(tracks=[])
#  average and find standard deviation

# print(sp.current_user())

# Olivia Rodrigo: '1McMsnEElThX1knmY4oliG'
# Pitbull: '0TnOYISbd1XYRBk9myaseg'
# Adele: '4dpARuHxo51G3z768sgnrY'
# Travis Scott: '0Y5tJX1MQlPlqiwlOH1tJY'
# artist_id = '0TnOYISbd1XYRBk9myaseg'

# Retrieve and return an artist's top tracks given a spotify artist ID
def getTrackIDs(artist_id):
    ids = []
    playlist = sp.artist_top_tracks(artist_id, country = 'US')
    # sp.user_playlist(user, playlist_id)
    
    for item in playlist['tracks']:
      #  track = item['track']
      ids.append(item['id'])
    return ids

# Given a spotify track ID, get its audio features
def getTrackFeatures(id):
    meta = sp.track(id)
    features = sp.audio_features(id)

    # meta
    # name = meta['name']
    # album = meta['album']['name']
    # artist = meta['album']['artists'][0]['name']
    # release_date = meta['album']['release_date']
    duration_ms = meta['duration_ms']
    # popularity = meta['popularity']

    # features
    acousticness = features[0]['acousticness']
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    loudness = features[0]['loudness']
    speechiness = features[0]['speechiness']
    key = features[0]['key']
    mode = features[0]['mode']
    tempo = features[0]['tempo']
    valence = features[0]['valence']
    time_signature = features[0]['time_signature']
    chorus_hit = None # features[0]['chorus_hit']
    sections = None # features[0]['sections']
    target = None # features[0]['target']

    # missing key, mode, valence
    track = [
        danceability, energy, key, loudness, mode, speechiness, 
        acousticness, instrumentalness, liveness, valence, tempo, 
        duration_ms, time_signature, chorus_hit, sections, target
    ]

    return track

def avg(feature):
    feature_adapted = []
    for k in feature:
        if k is not None:
            feature_adapted.append(k)
    if len(feature_adapted) == 0:
        return None
    return float(sum(feature_adapted)/len(feature_adapted))

def sd(feature):
    feature_adapted = []
    for k in feature:
        if k is not None:
            feature_adapted.append(k)
    if len(feature_adapted) == 0:
        return None
    return float(np.std(np.array(feature_adapted)))

# Given a spotify artist ID, get their audio features and add to database
def get_artist_info(artist_id, spotify_name, genres, followers, popularity):
    tracks = []
    ids = getTrackIDs(artist_id)
    for i in range(len(ids)):
        time.sleep(.5)
        track = getTrackFeatures(ids[i])
        tracks.append(track)
    
    # track = [
    #   danceability, energy, key, loudness, mode, speechiness, 
    #   acousticness, instrumentalness, liveness, valence, tempo, 
    #   duration_ms, time_signature, chorus_hit, sections, target
    # ]
    num_attrs = 16
    # num_attrs = len(tracks[0])
    # print(tracks)
    # print([[t[attr_i] for t in tracks] for attr_i in range(num_attrs)])
    means = [avg([t[attr_i] for t in tracks]) for attr_i in range(num_attrs)]
    sds = [sd([t[attr_i] for t in tracks]) for attr_i in range(num_attrs)]

    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                    INSERT INTO spotify_artist(spotify_id, spotify_name, genres, followers, popularity, mean_danceability, sd_danceability, mean_energy, sd_energy, mean_key, sd_key, mean_loudness, sd_loudness, mean_mode, sd_mode, mean_speechiness, sd_speechiness, mean_acousticness, sd_acousticness, mean_instrumentalness, sd_instrumentalness, mean_liveness, sd_liveness, mean_valence, sd_valence, mean_tempo, sd_tempo, mean_duration_ms, sd_duration_ms, mean_time_signature, sd_time_signature, mean_chorus_hit, sd_chorus_hit, mean_sections, sd_sections, mean_target, sd_target)
                    VALUES(:spotify_id, :spotify_name, :genres, :followers, :popularity, :mean_danceability, :sd_danceability, :mean_energy, :sd_energy, :mean_key, :sd_key, :mean_loudness, :sd_loudness, :mean_mode, :sd_mode, :mean_speechiness, :sd_speechiness, :mean_acousticness, :sd_acousticness, :mean_instrumentalness, :sd_instrumentalness, :mean_liveness, :sd_liveness, :mean_valence, :sd_valence, :mean_tempo, :sd_tempo, :mean_duration_ms, :sd_duration_ms, :mean_time_signature, :sd_time_signature, :mean_chorus_hit, :sd_chorus_hit, :mean_sections, :sd_sections, :mean_target, :sd_target)
                    RETURNING spotify_id
                    """).params(
                        spotify_id=artist_id,
                        spotify_name=spotify_name,
                        genres=genres,
                        followers=float(followers),
                        popularity=int(popularity),
                        mean_danceability=means[0],
                        sd_danceability=sds[0],
                        mean_energy=means[1],
                        sd_energy=sds[1],
                        mean_key=means[2],
                        sd_key=sds[2],
                        mean_loudness=means[3],
                        sd_loudness=sds[3],
                        mean_mode=means[4],
                        sd_mode=sds[4],
                        mean_speechiness=means[5],
                        sd_speechiness=sds[5],
                        mean_acousticness=means[6],
                        sd_acousticness=sds[6],
                        mean_instrumentalness=means[7],
                        sd_instrumentalness=sds[7],
                        mean_liveness=means[8],
                        sd_liveness=sds[8],
                        mean_valence=means[9],
                        sd_valence=sds[9],
                        mean_tempo=means[10],
                        sd_tempo=sds[10],
                        mean_duration_ms=means[11],
                        sd_duration_ms=sds[11],
                        mean_time_signature=means[12],
                        sd_time_signature=sds[12],
                        mean_chorus_hit=means[13],
                        sd_chorus_hit=sds[13],
                        mean_sections=means[14],
                        sd_sections=sds[14],
                        mean_target=means[15],
                        sd_target=sds[15]))
    except exc.IntegrityError:
        logger.spotify_warn("There was a duplicate spotify artist for {:} {:}".format(artist_id, spotify_name))
    return artist_id

# timebox and extract spotify and twitter information
def extract_all(spotify_missing_offset=0, spotify_follower_offset=0):
    missing_artists_df = pd.read_csv(MISSING_ARTISTS_CSV, header=None, skiprows=spotify_missing_offset)
    missing_artists_follower_df = pd.read_csv(MISSING_ARTISTS_CSV, header=None, skiprows=spotify_follower_offset)

    missing_artists_max = missing_artists_df.index.stop
    missing_artists_follower_max = missing_artists_max

    u_count = 0
    f_count = 0
    f_ind_follower_iter = 0

    last_user_time = 0.0
    last_following_time = 0.0

    next_token = ""

    while True:
    # for k in range(1):

        # spotify and user queries
        # 300 per 15 minute, 20 per minute, 1 per 3 seconds
        for k in range(20):
            # print(u_count)

            u_ind = u_count
            if u_ind >= missing_artists_max:
                break
            u_spotify_id = missing_artists_df.iloc[u_ind, 0]
            u_spotify_name = missing_artists_df.iloc[u_ind, 1]
            u_spotify_genres = missing_artists_df.iloc[u_ind, 2]
            u_spotify_followers = missing_artists_df.iloc[u_ind, 3]
            u_spotify_popularity = missing_artists_df.iloc[u_ind, 4]

            # Get track features, create artist
            # TODO: ADD ERROR HANDLING, RATE LIMITING AS NECESSARY
            get_artist_info(u_spotify_id, u_spotify_name, u_spotify_genres, u_spotify_followers, u_spotify_popularity)

            curr_time = time.time()
            diff_delay = curr_time - last_user_time - 3
            if diff_delay < 0:
                time.sleep(-1*diff_delay + 0.1)

            if u_count % 10 == 0:
                logger.twitter_debug("Parsing {:}th artist for HTML, {:}".format(u_count, u_spotify_name))

            # spotify_id -> twitter_username
            u_twitter_username = extract_twitter_id(u_spotify_id, SPOTIFY_MISSING_TWITTER_FILE_2)
            if u_twitter_username == -1:
                u_count += 1
                continue

            # twitter_username, spotify_id -> twitter_id, @write(twitter_user)
            u_twitter_id = extract_base_twitter_info(u_twitter_username, u_spotify_id, engine)
            # print(u_twitter_id, u_spotify_id, u_spotify_name)
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
        f_ind = f_count
        if f_ind >= missing_artists_follower_max:
            break
        f_spotify_id = missing_artists_follower_df.iloc[f_ind, 0]
        f_spotify_name = missing_artists_follower_df.iloc[f_ind, 1]

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
            FileWrapper.appendToFile(SPOTIFY_MISSING_TWITTER_FILE_2, "{:},{:},".format(f_spotify_id, f_spotify_name))
            continue

        if next_token is None:
            next_token = ""
        # twitter_id, next_token='' -> following_user_list, next_token, @write(twitter_user, following)
        following_user_list, next_token = extract_twitter_following_info(f_twitter_id, next_token, engine)
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
            FileWrapper.writeValToFile(MISSING_SONG_ATTRIBUTES_FILE, u_count+spotify_missing_offset)
            FileWrapper.writeValToFile(MISSING_SONG_FOLLOWERS_FILE, f_count+spotify_follower_offset)

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
        logger.spotify_warn("Bad argument: {:} {:}".format(sys.argv[1] if len(sys.argv) > 1 else "missing", sys.argv[2] if len(sys.argv) > 2 else "missing"))
        sys.exit()
    spotify_missing_artist = int(sys.argv[1])
    if spotify_missing_artist < 0:
        spotify_missing_artist = 0
    elif spotify_missing_artist > 400000:
        logger.spotify_info("Argument too large, skipping", spotify_missing_artist)
        sys.exit()
    spotify_missing_followers = int(sys.argv[2])
    if spotify_missing_followers < 0:
        spotify_missing_followers = 0
    elif spotify_missing_followers > 400000:
        logger.spotify_info("Argument too large, skipping", spotify_missing_followers)
        sys.exit()

    logger.spotify_info("Beginning spotify parsing with {:} {:}".format(spotify_missing_artist, spotify_missing_followers))
    extract_all(spotify_missing_artist, spotify_missing_followers)


