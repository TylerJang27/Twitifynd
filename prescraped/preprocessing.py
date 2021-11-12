
# import packages
from collections import defaultdict

import seaborn as sns
import pandas as pd
pd.set_option('display.max_columns', 8)
pd.set_option('display.max_rows', 5)
import json
# import matplotlib.pyplot as plt
import numpy as np

# read in the data
artists = pd.read_csv("artists.csv")
dataset_00s = pd.read_csv("dataset-of-00s.csv")
dataset_10s = pd.read_csv("dataset-of-10s.csv")
dataset_90s = pd.read_csv("dataset-of-90s.csv")
dataset_80s = pd.read_csv("dataset-of-80s.csv")
dataset_70s = pd.read_csv("dataset-of-70s.csv")
dataset_60s = pd.read_csv("dataset-of-60s.csv")

data = pd.concat([dataset_00s, dataset_60s, dataset_80s ,dataset_90s ,dataset_70s ,dataset_10s])


# print(artists)
mean_of_artists = data.groupby("artist").mean()
std_of_artists = data.groupby("artist").std()
mean_of_artists.to_json("means.json")
std_of_artists.to_json("std.json")
# print(std_of_artists)
# print(data.groupby("artist").mean())

f = open('std.json')
std = json.load(f)

f = open('means.json')
averages = json.load(f)

result = defaultdict(dict)

artist_result = []
missing_artists = []

df = pd.read_csv("artists.csv")
artists_avail = averages['danceability']
count = 0

for ind in df.index:
    count += 1
    if count % 10000 == 0:
        print(count)
    spotify_id = df.iloc[ind, 0]
    spotify_followers = df.iloc[ind, 1]
    spotify_genres = df.iloc[ind, 2]
    spotify_name = df.iloc[ind, 3]
    spotify_popularity = df.iloc[ind, 4]

    if spotify_name in artists_avail:        
        da_m = averages["danceability"][spotify_name]
        da_sd = std["danceability"][spotify_name]
        en_m = averages["energy"][spotify_name]
        en_sd = std["energy"][spotify_name]
        ke_m = averages["key"][spotify_name]
        ke_sd = std["key"][spotify_name]
        lo_m = averages["loudness"][spotify_name]
        lo_sd = std["loudness"][spotify_name]
        mo_m = averages["mode"][spotify_name]
        mo_sd = std["mode"][spotify_name]
        sp_m = averages["speechiness"][spotify_name]
        sp_sd = std["speechiness"][spotify_name]
        ac_m = averages["acousticness"][spotify_name]
        ac_sd = std["acousticness"][spotify_name]
        in_m = averages["instrumentalness"][spotify_name]
        in_sd = std["instrumentalness"][spotify_name]
        li_m = averages["liveness"][spotify_name]
        li_sd = std["liveness"][spotify_name]
        va_m = averages["valence"][spotify_name]
        va_sd = std["valence"][spotify_name]
        te_m = averages["tempo"][spotify_name]
        te_sd = std["tempo"][spotify_name]
        du_m = averages["duration_ms"][spotify_name]
        du_sd = std["duration_ms"][spotify_name]
        ts_m = averages["time_signature"][spotify_name]
        ts_sd = std["time_signature"][spotify_name]
        ch_m = averages["chorus_hit"][spotify_name]
        ch_sd = std["chorus_hit"][spotify_name]
        se_m = averages["sections"][spotify_name]
        se_sd = std["sections"][spotify_name]
        ta_m = averages["target"][spotify_name]
        ta_sd = std["target"][spotify_name]
        
        artist_result.append([spotify_id, spotify_name, spotify_genres, spotify_followers, spotify_popularity, da_m, da_sd, en_m, en_sd, ke_m, ke_sd, lo_m, lo_sd, mo_m, mo_sd, sp_m, sp_sd, ac_m, ac_sd, in_m, in_sd, li_m, li_sd, va_m, va_sd, te_m, te_sd, du_m, du_sd, ts_m, ts_sd, ch_m, ch_sd, se_m, se_sd, ta_m, ta_sd])
    else:
        missing_artists.append([spotify_id, spotify_name, spotify_genres, spotify_followers, spotify_popularity])
df_artist_results = pd.DataFrame(artist_result)
header = ["id", "name", "genres", "followers", "popularity", "mean_danceability", "sd_danceability", "mean_energy", "sd_energy", "mean_key", "sd_key", "mean_loudness", "sd_loudness", "mean_mode", "sd_mode", "mean_speechiness", "sd_speechiness", "mean_acousticness", "sd_acousticness", "mean_instrumentalness", "sd_instrumentalness", "mean_liveness", "sd_liveness", "mean_valence", "sd_valence", "mean_tempo", "sd_tempo", "mean_duration_ms", "sd_duration_ms", "mean_time_signature", "sd_time_signature", "mean_chorus_hit", "sd_chorus_hit", "mean_sections", "sd_sections", "mean_target", "sd_target"]
df_artist_results.columns = header
df_artist_results = df_artist_results.sort_values(by=["popularity", "followers", "genres", "name"], ascending=False)
df_artist_results.to_csv('artist_result.csv', index=False, header=header)

df_missing_artists = pd.DataFrame(missing_artists)
header = ["id", "name", "genres", "followers", "popularity"]
df_missing_artists.columns = header
df_missing_artists = df_missing_artists.sort_values(by=["popularity", "followers", "genres", "name"], ascending=False)
df_missing_artists.to_csv('missing_artists.csv', index=False, header=header)

# header = ["id", "name", "genres", "followers", "mean_danceability", "sd_danceability", "mean_energy", "sd_energy", "mean_key", "sd_key", "mean_loudness", "sd_loudness", "mean_mode", "sd_mode", "mean_speechiness", "sd_speechiness", "mean_acousticness", "sd_acousticness", "mean_instrumentalness", "sd_instrumentalness", "mean_liveness", "sd_liveness", "mean_valence", "sd_valence", "mean_tempo", "sd_tempo", "mean_duration_ms", "sd_duration_ms", "mean_time_signature", "sd_time_signature", "mean_chorus_hit", "sd_chorus_hit", "mean_sections", "sd_sections", "mean_target", "sd_target"]
# df_artist_results = pd.read_csv("artist_result.csv")
# df_artist_results = df_artist_results.sort_values(by=["popularity", "followers", "genres", "name"], ascending=False)
# df_artist_results.to_csv('artist_result2.csv', index=False, header=header)

# header = ["id", "name", "genres", "followers"]
# df_missing_artists = pd.read_csv("missing_artists.csv")
# df_missing_artists = df_missing_artists.sort_values(by=["followers", "genres", "name"], ascending=False)
# df_missing_artists.to_csv('missing_artists_popular.csv', index=False, header=header)


# for feature in averages:
#     for artist in averages[feature]:
#         result[artist][feature] = [averages[feature][artist], std[feature][artist]]

# print(result)
# print("Number of Artists: {}".format(len(result)))
# print("Number of songs: {}".format(len(data)))
# with open("artist_averages.json", "w") as outfile:
#     json.dump(result, outfile)

