from ..utils.utils import EmailWrapper, FileWrapper, LoggerWrapper
import sys

if __name__ == "__main__":
    logger=LoggerWrapper()
    if len(sys.argv) <= 1 or sys.argv[1] != "":
        logger.twitter_warn("Bad argument: ", sys.argv[1] if len(sys.argv) > 1 else "missing")
        sys.exit()
    artist_result_offset = sys.argv[1]
    if artist_result_offset < 0:
        artist_result_offset = 0
    elif artist_result_offset > 20000:
        logger.twitter_info("Argument too large, skipping", artist_result_offset)
        sys.exit()
    # TODO: ADD ONE MORE CHECK AGAINST THE TWITTER_USER TABLE
    
    logger.twitter_info("Beginning twitter parsing")
