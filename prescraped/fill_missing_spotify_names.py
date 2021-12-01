import os
import pandas as pd
import numpy as np

def get_names():
    header = ["id", "name", "genres", "followers", "popularity"]

    missing_artists = pd.read_csv("missing_artists.csv", header=None)
    missing_artists.columns = header
    df = pd.read_csv("missing_twitter_2.csv", header=None)
    artist_names = pd.Series(missing_artists["name"]).unique()

    for ind in df.index:
        if ind % 100 == 0:
            print(ind)
        spotify_id = df.iloc[ind, 0]
        artist_name = missing_artists.loc[missing_artists['id'] == spotify_id]['name'].values[0]
        df.iloc[ind, 1] = artist_name

    df.to_csv('missing_twitter_2_fixed.csv', index=False, header=None)

def remove_sci_not():
    df = pd.read_csv("missing_twitter_with_handles2_bak.csv", header=None)
    df.columns = ["spotify_id", "name", "handle", "twitter_id", "blah"]
    df = df.astype({'blah': 'float64', 'twitter_id': 'float64'})

    for ind in df.index:
        if df.iloc[ind, 3] == "" or df.iloc[ind, 3] == 0 or pd.isnull(df.iloc[ind, 3]):
            df.iloc[ind, 3] = df.iloc[ind, 4]
            if ind < 5:
                print(df.iloc[ind,])
    df = df.fillna(0)
    df = df.drop(columns=["blah"])
    df = df.astype({'twitter_id': 'float'})
    df = df.astype({'twitter_id': 'uint64'})
    df.to_csv('missing_twitter_with_handles2.csv', index=False, header=None)

# for columns with just spotify_id, get the spotify_name
if __name__ == "__main__":
    #get_names()
    remove_sci_not()

    
    