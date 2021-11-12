from ..utils.utils import Config, EmailWrapper, FileWrapper, LoggerWrapper
import sys
import pandas as pd

ARTIST_RESULT_CSV = "/code/prescraped/artist_result.csv"
logger=LoggerWrapper()

def extract_twitter_id(spotify_id):
    # TODO: USE BEAUTIFUL SOUP OR SOMETHING, USE THE WEB URI AND SCRAPE FOR THE TWITTER FIELD IN THE DESCRIPTION/BIO
    # may need to convert to int
    # also handle request error codes as necessary
    return None

def extract_twitter_info(twitter_id):
    # TODO: USE REQUESTS TO QUERY TWITTER API FOR FOLLOWER/FOLLOWING INFO AS DESIRED, SEE twitter_scraper.py FOR REFERENCE
    return None

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
