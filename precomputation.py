import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import json

with open('prescraped/artist_result.csv') as c:
    table = pd.read_csv(c)

popular = table[table.iloc[:, 4] >= 65]
candidates = table[table.iloc[:,4]<65]

popular_ids = set()
for pid in popular.iloc[:,0]:
    popular_ids.add(pid)
candidates_ids = set()
for cid in candidates.iloc[:,0]:
    candidates_ids.add(cid)

means_cols = []
for i in range(5,table.shape[1],2):
    means_cols.append(i)

artist_info = {}
genres = set()
for i, row in table.iterrows():
    #both = np.array(row.iloc[5:])
    means = []
    for col in means_cols:
        means.append(row.iloc[col])
    artist_genres = []
    for g in row.iloc[2].replace('[', '').replace(']','').replace("'", "").split(','):
        genres.add(g.strip())
        artist_genres.append(g.strip())
    artist_info[row.iloc[0]] = {'name': row.iloc[1], 'followers': int(row.iloc[3]),
                                'means': means, 'genres': artist_genres}
    

data_means = table.iloc[:,means_cols]
#data_both = table.iloc[:,5:]
num_clust = math.floor(popular.shape[0]/2)

means_clusters = KMeans(n_clusters=num_clust, init='k-means++').fit(data_means)


for i, row in table.iterrows():
    artist_info[row.iloc[0]]['cluster'] = means_clusters.labels_[i].item()

df_artists_clusters = pd.DataFrame(columns=['id', 'cluster'])
for artist in artist_info:
    df_artists_clusters = df_artists_clusters.append({'id': artist, 'cluster': artist_info[artist]['cluster']}, ignore_index=True)

clusters_groups = df_artists_clusters.groupby(['cluster'])

popular_candidates = {}
for pid in popular.iloc[:,0]:
    popular_candidates[pid] = []

for cluster in range(num_clust):
    g = clusters_groups.get_group(cluster)
    p = []
    c = []
    for id in g.loc[:,'id']:
        if id in popular_ids:
            p.append(id)
        elif id in candidates_ids:
            c.append(id)
        else:
            print('neither')
    for pid in p:
        for cid in c:
            popular_candidates[pid].append(cid)

candidates_scores = {}
for pid in popular_candidates:
    candidates = popular_candidates[pid]
    candidates_scores[pid] = []
    for cid in candidates:
        similarity = np.linalg.norm(np.array(artist_info[pid]['means']) - np.array(artist_info[cid]['means'])).item()
        cf = artist_info[cid]['followers']
        pf = artist_info[pid]['followers']
        if cf==0:
            popularity = 0
        else:
            popularity = math.log(cf) / math.log(pf)
        novelty = 1 - popularity
        score = similarity*novelty
        candidates_scores[pid].append(tuple((cid, score)))

with open('precomputed/artist_info.json', 'w') as ai_file:
    json.dump(artist_info, ai_file)
with open('precomputed/candidates_scores.json', 'w') as cs_file:
    json.dump(candidates_scores, cs_file)
