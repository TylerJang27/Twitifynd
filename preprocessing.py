# import packages
from collections import defaultdict, Counter

# import seaborn as sns
import pandas as pd

pd.set_option('display.max_columns', 8)
pd.set_option('display.max_rows', 5)
import json
import matplotlib.pyplot as plt
import numpy as np

# read in the data
artists = pd.read_csv("artists.csv")
dataset_00s = pd.read_csv("dataset-of-00s.csv")
dataset_10s = pd.read_csv("dataset-of-10s.csv")
dataset_90s = pd.read_csv("dataset-of-90s.csv")
dataset_80s = pd.read_csv("dataset-of-80s.csv")
dataset_70s = pd.read_csv("dataset-of-70s.csv")
dataset_60s = pd.read_csv("dataset-of-60s.csv")

data = pd.concat([dataset_00s, dataset_60s, dataset_80s, dataset_90s, dataset_70s, dataset_10s])

# filter by genre
set_genres = []
data = pd.merge(artists, data, left_on="name", right_on="artist")
for genre in data['genres']:
    for ind_genre in list(genre.strip("[").strip("]").strip(" ").split(",")):
        if ind_genre:
            set_genres.append(ind_genre.strip(" ").strip("\'"))

set_genres = Counter(set_genres).most_common()

# print(len(set_genres))
print(set_genres)
# print(len(data))

#filter by genre
# gapminder_2002 = gapminder[gapminder['year']==2002]


# DO NOT CHANGE OTHER PARTS OF THE CODE
# ONLY THING TO CHANGE IS THE KEY VALUE
# SELECT A KEY FROM THE `set_genres` set
key = "dance pop"


## DO NOT MODIFY ANYTHING BELOW
data = data[data['genres'].str.contains(key)]
# print(data)
#
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

for feature in averages:
    for artist in averages[feature]:
        result[artist][feature] = [averages[feature][artist], std[feature][artist]]

# print(result)
print("Number of Artists: {}".format(len(result)))
print("Number of songs: {}".format(len(data)))
with open("artist_averages_{}.json".format(key), "w") as outfile:
    json.dump(result, outfile)
