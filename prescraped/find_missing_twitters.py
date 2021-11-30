#!/usr/bin/env python3

import pandas as pd
import requests
import time
import json
import os

headers = {"Authorization": "Bearer {:}".format('')}

if __name__ == "__main__":
    df = pd.read_csv("missing_twitter_fixed.csv", header=None)

    df.insert(3, "twitter_id", ['' for k in df.index], True)
    last_time = 0

    for ind in df.index:
        if ind < 5000:
            continue
        if (ind + 1) % 500 == 0:
            print("Saving to csv")
            df.to_csv("missing_twitter_with_handles2.csv", index = False, header = None)
        if ind % 25 == 0:
            print(ind)
        s = str(df.iloc[ind, 1]).strip().replace(" ", "").replace(".", "").replace("&", "").replace("-", "").lower()
        twitter_user_request_string = 'https://api.twitter.com/2/users/by/username/{:}?user.fields=id,name,verified,description,protected,public_metrics,location'
        curr_time = time.time()
        diff_delay = curr_time - last_time - 3
        if diff_delay < 0:
            time.sleep(-1*diff_delay + 0.1)
        user_r = requests.get(twitter_user_request_string.format(s), headers=headers)
        last_time = time.time()

        if user_r.status_code != 200:
            print("Unable to perform HTTP request for ID: {:}".format(s))
            print("Status code: ", user_r.status_code)
            continue

        json_data = json.loads(user_r.text)

        if 'errors' in json_data:
            print("Unable to find ID: {:}".format(s))
            continue
        # print(json_data)
        if not json_data["data"]["verified"] and json_data["data"]["public_metrics"]["followers_count"] < 10000:
            print("User {:} does not meet arbitrary criteria".format(json_data["data"]["username"]))
            continue

        df.iloc[ind, 2] = json_data["data"]["username"]
        df.iloc[ind, 3] = json_data["data"]["id"]

    df.to_csv("missing_twitter_with_handles2.csv", index = False, header = None)
