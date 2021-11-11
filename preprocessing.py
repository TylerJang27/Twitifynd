
# import packages
from collections import defaultdict

import seaborn as sns
import pandas as pd
pd.set_option('display.max_columns', 8)
pd.set_option('display.max_rows', 5)
import json
import matplotlib.pyplot as plt
import numpy as np
g
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

for feature in averages:
    for artist in averages[feature]:
        result[artist][feature] = [averages[feature][artist], std[feature][artist]]

print(result)
print("Number of Artists: {}".format(len(result)))
print("Number of songs: {}".format(len(data)))
with open("artist_averages.json", "w") as outfile:
    json.dump(result, outfile)
