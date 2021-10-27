#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
In order to run this script, first run:
    pip install python-dotenv
    cp template.env .env # edit it to contain the Twitter Bearer token
    
'''

import os
from sys import exit
from dotenv import dotenv_values
import requests
import time

TWITTER_FOLLOWERS_URL = "https://api.twitter.com/2/users/{:}/followers"

def get_bearer():
    config = dotenv_values(".env")
    if len(config) == 0:
        print("Please create your .env file")
        exit()
    
    if not 'TWITTER_BEARER' in config:
        print("Please add your TWITTER_BEARER token to your .env file")
        exit()
            
    twitter_bearer = config['TWITTER_BEARER']
    
    if twitter_bearer == "default_secret":
        print("Please add your TWITTER_BEARER token to your .env file")
        exit()
    return twitter_bearer



def request_to_api(url, bearer):
    headers = {"Authorization": "Bearer {:}".format(bearer)}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("ERROR: STATUS CODE: {:}".format(response.status_code))

def request_followers(user_id, bearer):
    return request_to_api(TWITTER_FOLLOWERS_URL.format(user_id), bearer)


if __name__ == "__main__":
    twitter_bearer = get_bearer()
    quinn_followers = request_followers(714845064, twitter_bearer)
    print(quinn_followers)
    