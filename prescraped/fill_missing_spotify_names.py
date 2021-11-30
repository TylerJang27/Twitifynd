import os
import pandas as pd

# for columns with just spotify_id, get the spotify_name
if __name__ == "__main__":
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
    