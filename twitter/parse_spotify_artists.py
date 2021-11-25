from ..utils.utils import Config, EmailWrapper, FileWrapper, LoggerWrapper
import sys
import pandas as pd
import requests

ARTIST_RESULT_CSV = "/code/prescraped/artist_result.csv"
logger=LoggerWrapper()

def extract_twitter_id(spotify_id):
    # TODO: USE BEAUTIFUL SOUP OR SOMETHING, USE THE WEB URI AND SCRAPE FOR THE TWITTER FIELD IN THE DESCRIPTION/BIO
    # may need to convert to int
    # also handle request error codes as necessary

    r = requests.get('https://open.spotify.com/artist/{:}'.format(spotify_id))

    if r.status_code != 200:
        logger.twitter_warn("Unable to perform HTTP request for ID: {:}".format(spotify_id))

    # {"name":"TWITTER","url":"https://twitter.com/justinbieber"}
    try:
        twitter_id = r.text.split('{"name":"TWITTER","url":"https://twitter.com/')[1].split('"')[0]
    except IndexError:
        logger.twitter_warn("User has not connected their Spotify to Twitter")
        return -1

    return twitter_id

def extract_twitter_info(twitter_id):
    headers = {"Authorization": "Bearer {:}".format($TWITTER_BEARER)}

    user_id_r = requests.get('https://api.twitter.com/2/users/by/username/{:}'.format(twitter_id), headers=headers)
    
    if user_id_r.status_code != 200:
        logger.twitter_warn("Unable to perform HTTP request for ID: {:}".format(twitter_id))
    
    user_id = int(json.loads(user_id_r.text)['data']['id'])
    
    followers_r = requests.get('https://api.twitter.com/2/users/{:}/following'.format(user_id), headers=headers)
    
    if user_id_r.status_code != 200:
        logger.twitter_warn("Unable to perform HTTP request for ID: {:}".format(user_id))
    
    data = json.loads(followers_r.text)['data']
    
    list_of_ids = []
    
    for i in data:
        list_of_ids += [i['username']]
    
    return list_of_ids

def extract_all(offset=0):
    artist_result_csv = pd.read_csv(ARTIST_RESULT_CSV, skiprows=offset)
    count_rows_parsed = 0
    count_twitter_extracted = 0

    for ind in df.index:
        spotify_id = df.iloc[ind, 0]
        spotify_name = df.iloc[ind, 1]
        # TODO: EXTRACT OTHER FIELDS AS NECESSARY, SEE preprocessing.py

        if count % 10 == 0:
            logger.twitter_debug("Parsing {:}th artist for HTML, {:}".format(count, spotify_name))
        count += 1

        twitter_id = extract_twitter_id(spotify_id)
        if twitter_id is None:
            logger.twitter_debug("Unable to retrieve twitter_id for {:} : {:}".format(spotify_id, spotify_name))
            continue

        twitter_info = extract_twitter_info(twitter_id) # TODO: TIMEBOX
        if twitter_info is None:
            logger.twitter_warn("Unable to retrieve twitter info for {:} : {:} with twitter handle {:}".format(spotify_id, spotify_name, twitter_id))
            continue
        
        # TODO: WRITE TO DATABASE, POTENTIALLY SEE 316 CODE FOR SAMPLES, MAY BE USEFUL TO ADD DBWrapper AS A CLASS TO utils.py
        count_twitter_extracted += 1


        if count % 100 == 0:
           logger.twitter_debug("Exporting for safety at count of {:}".format(count))
            # TODO: at some point, periodically, call FileWrapper.writeValToFile(ARTIST_RESULT_FILE, count_rows_parsed+offset)

            # TODO: at some point, periodically, call /bin/bash /db/export.sh and then take the resulting exported csvs and email them using EmailWrapper (you will have to get the filepaths somehow)
        # TODO: PROBS ADD A WAIT HERE FOR TIMEBOXING

if __name__ == "__main__":
    if len(sys.argv) <= 1 or sys.argv[1] != "":
        logger.twitter_warn("Bad argument: ", sys.argv[1] if len(sys.argv) > 1 else "missing")
        sys.exit()
    artist_result_offset = sys.argv[1]
    if artist_result_offset < 0:
        artist_result_offset = 0
    elif artist_result_offset > 20000:
        logger.twitter_info("Argument too large, skipping", artist_result_offset)
        sys.exit()
    # TODO: ADD ONE MORE CHECK AGAINST THE TWITTER_USER TABLE TO AVOID REQUERYING INFO
    
    logger.twitter_info("Beginning twitter parsing with {:}".format(artist_result_offset))
    extract_all(artist_result_offset)
    # TODO: @JUSTIN @ANDREW
