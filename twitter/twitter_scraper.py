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

config = dotenv_values(".env")
if len(config) == 0:
    print("Please create your .env file")
    exit()

if not 'TWITTER_BEARER' in config:
    print("Please add your TWITTER_BEARER token to your .env file")
    exit()
        
TWITTER_BEARER = config['TWITTER_BEARER']

if TWITTER_BEARER == "default_secret":
    print("Please add your TWITTER_BEARER token to your .env file")
    exit()

