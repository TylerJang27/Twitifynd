#!/usr/bin/env python3
import logging
from logging import config
import os
from os import path
import sys
import ntpath
import smtplib
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LOG_PATH = '/data/script_logs/'
SENDER_EMAIL = 'twitifynd@example.com'
MAIL_SERVER_HOSTNAME = 'mail'

class Config(object):
    TWITTER_BEARER = os.environ.get('TWITTER_BEARER')
    SPOTIFY_ID = os.environ.get('SPOTIFY_ID')
    SPOTIFY_SECRET = os.environ.get('SPOTIFY_SECRET')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@localhost/{}'\
        .format(os.environ.get('POSTGRES_USER'),
                os.environ.get('PGPASSWORD'),
                os.environ.get('POSTGRES_DB'))
    RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LoggerWrapper:
    twitter_logger = None
    spotify_logger = None
    db_logger = None
    mgr_logger = None
    email_logger = None

    def __init__(self):
        os.getcwd()
        config_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
        config.fileConfig(config_file_path)

        self.mgr_logger = logging.getLogger("mgr")
        self.twitter_logger = logging.getLogger("twitter")
        self.spotify_logger = logging.getLogger("spotify")
        self.db_logger = logging.getLogger("db")
        self.email_logger = logging.getLogger("email")

    def twitter_info(self, message):
        self.twitter_logger.info(message)

    def twitter_debug(self, message):
        self.twitter_logger.debug(message)

    def twitter_warn(self, message):
        self.twitter_logger.warning(message)

    def spotify_info(self, message):
        self.spotify_logger.info(message)

    def spotify_debug(self, message):
        self.spotify_logger.debug(message)

    def spotify_warn(self, message):
        self.spotify_logger.warning(message)

    def db_info(self, message):
        self.db_logger.info(message)

    def db_debug(self, message):
        self.db_logger.debug(message)

    def db_warn(self, message):
        self.db_logger.warning(message)
    
    def manager_info(self, message):
        self.mgr_logger.info(message)

    def manager_debug(self, message):
        self.mgr_logger.debug(message)

    def manager_warn(self, message):
        self.mgr_logger.warning(message)
    
    def email_warn(self, message):
        self.email_logger.warning(message)


class EmailWrapper:
    @staticmethod
    def sendEmail(body, subject="Twitifynd Alert", attachment=""):
        smtp_server = MAIL_SERVER_HOSTNAME
        sender_email = SENDER_EMAIL
        receiver_email = Config.RECEIVER_EMAIL

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        if attachment != "":
            _, filetail = ntpath.split(attachment)
            with open(attachment, "rb") as attachment_data:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_data.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {filetail}")
            message.attach(part)
        
        text = message.as_string()
        with smtplib.SMTP(smtp_server, 25) as server:
            server.sendmail(sender_email, receiver_email, text)

if __name__ == "__main__":

    logger = LoggerWrapper()
    # logger.manager_info("Default run of utils")
    artist_result_line = sys.argv[1] if len(sys.argv) > 1 else "Missing"
    artist_id = sys.argv[1] if len(sys.argv) > 1 else "Missing"
    missing_song_attributes = sys.argv[1] if len(sys.argv) > 1 else "Missing"
    twitter_user_queue = sys.argv[1] if len(sys.argv) > 1 else "Missing"
    body = "Twitifynd starting up.\nArtist Result Line: {:}\nArtist ID: {:}\nMissing Song Attributes: {:}\nTwitter User Queue: {:}".format(artist_result_line, artist_id, missing_song_attributes, twitter_user_queue)
    logger.email_warn(body)

    # filename = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
    # EmailWrapper.sendEmail("Test Email", attachment=filename)