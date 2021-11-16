from utils import LoggerWrapper
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "":
        logger = LoggerWrapper()
        body = sys.argv[1]
        logger.email_warn(body)