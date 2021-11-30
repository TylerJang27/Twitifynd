import numpy as np
import pandas as pd
import math
from sklearn.cluster import KMeans
import json

# artists
with open('log_2021-11-29_05_34_18/artist.csv') as a:
    artists = pd.read_csv(a, header=None)
# following
with open('log_2021-11-29_05_34_18/following.csv') as f:
    following = pd.read_csv(f, header=None)
# spotify
with open('log_2021-11-29_05_34_18/spotify_artist.csv') as s:
    spotify = pd.read_csv(s, header=None)
means_cols = []
# audio features up to duration
for i in range(5, 27, 2):
    # omit key
    if i == 9:
        pass
    else:
        means_cols.append(i)
# twitter
with open('log_2021-11-29_05_34_18/twitter_user.csv') as t:
    twitter = pd.read_csv(t, header=None)

# check for nan and finite columns
for col in means_cols:
    col_nan = np.isnan(spotify.iloc[:, col]).values.any()
    if col_nan is True:
        print('Column {} has nan'.format(col))
    col_inf = np.isinf(spotify.iloc[:, col]).values.any()
    if col_inf is True:
        print('Column {} has inf'.format(col))
    col_large = (spotify.iloc[:, col] >= np.finfo('float64').max).any()
    if col_large is True:
        print('Column {} has large value'.format(col))
#print('nan in spotify {}'.format(np.isnan(pd.DataFrame(np.nan_to_num(spotify.iloc[:, means_cols]))).values.any()))
#print('done with checks')

# spotify info dictionary
s_info = {}
sids = set()
tids = set()
# spotify id key, add twitter id
for i, row in artists.iterrows():
    s_info[row[2]] = {'tid': int(row[1])}
    sids.add(row[2])
    tids.add(int(row[1]))
print('{} unique spotify ids'.format(len(sids)))
print('{} unique twitter ids'.format(len(tids)))
# spotify name, genres, means
for i, row in spotify.iterrows():
    sid = row[0]
    if sid in s_info:
        s_info[sid]['spotify name'] = row[1]
        genres = []
        for g in row.iloc[2].replace('[', '').replace(']', '').replace("'", "").split(','):
            genres.append(g.strip())
        s_info[sid]['genres'] = genres
        means = []
        for col in means_cols:
            means.append(row.iloc[col])
        s_info[sid]['means'] = means

# twitter info dictionary
t_info = {}
# twitter id keys, add username, name, followers and following counts
for i, row in twitter.iterrows():
    t_info[int(row[0])] = {'username': row[1], 'name': row[2],
    'followers count': row[5], 'following count': row[6],
    'followers': [], 'following': []}
# followers and following ids
for i, row in following.iterrows():
    t_info[int(row[0])]['following'].append(int(row[1]))
    t_info[int(row[1])]['followers'].append(int(row[0]))
# artists and followers count table
df_artists_fcounts = pd.DataFrame(columns=['sid', 'tid', 'followers count'])
for sid in s_info:
    tid = s_info[sid]['tid']
    df_artists_fcounts = df_artists_fcounts.append(
        {'sid': sid, 'tid': tid, 'followers count': t_info[tid]['followers count']}, ignore_index=True)

# Popular vs candidate threshold
popular = df_artists_fcounts[df_artists_fcounts.iloc[:, 2] >= 100000]
popular_sids = set([psid for psid in popular.iloc[:,0]])
print('{} popular artists'.format(len(popular_sids)))
candidates = df_artists_fcounts[df_artists_fcounts.iloc[:, 2] < 100000]
candidates_sids = set([csid for csid in candidates.iloc[:, 0]])
print('{} candidate artists'.format(len(candidates_sids)))

# spotify means only, for clustering
cols_id_means = [0] + means_cols
spotify_means = spotify.iloc[:, cols_id_means]
for i, row in spotify_means.iterrows():
    if row[0] not in s_info:
        spotify_means.drop(i, inplace=True)
spotify_means.reset_index(drop=True, inplace=True)
spotify_means_clust = pd.DataFrame(np.nan_to_num(spotify_means.drop(0, axis=1)))
# clustering
num_clust = math.floor(popular.shape[0]/16)
print('{} clusters'.format(num_clust))
clusters = KMeans(n_clusters=num_clust, init='k-means++').fit(spotify_means_clust)
# add cluster group info
for i, row in spotify_means.iterrows():
    s_info[row.iloc[0]]['cluster'] = clusters.labels_[i].item()
# make sid and cluster group df
df_artists_clusters = pd.DataFrame(columns=['sid', 'cluster'])
for artist in s_info:
    df_artists_clusters = df_artists_clusters.append(
        {'sid': artist, 'cluster': s_info[artist]['cluster']}, ignore_index=True)
# group by cluster
clusters_groups = df_artists_clusters.groupby(['cluster'])
# make dictionary with:
# popular artist key
# candidate artists in same cluster
popular_candidates = {}
for psid in popular_sids:
    popular_candidates[psid] = []
for clust in range(num_clust):
    g = clusters_groups.get_group(clust)
    p = []
    c = []
    for sid in g.loc[:, 'sid']:
        if sid in popular_sids:
            p.append(sid)
        elif sid in candidates_sids:
            c.append(sid)
        else:
            print('neither')
    for psid in p:
        for csid in c:
            popular_candidates[psid].append(csid)
# calculate scores
candidates_scores = {}
for psid in popular_candidates:
    candidates = popular_candidates[psid]
    candidates_scores[psid] = []
    for csid in candidates:
        similarity = np.linalg.norm(np.array(s_info[psid]['means']) - np.array(s_info[csid]['means'])).item()        
        ctid = s_info[csid]['tid']
        ptid = s_info[psid]['tid']
        cf = t_info[ctid]['followers count']
        pf = t_info[ptid]['followers count']
        if cf == 0:
            popularity = 0
        else:
            popularity = math.log(cf) / math.log(pf)
        novelty = 1 - popularity
        score = similarity*novelty
        candidates_scores[psid].append(tuple((csid, score)))

# spotify name find
s_name_find = {}
for sid in s_info:
    name = s_info[sid]['spotify name']
    if name in s_name_find:
        s_name_find[name].append(sid)
    else:
        s_name_find[name] = [sid]
# twitter username find
t_uname_find = {}
for sid in s_info:
    tid = s_info[sid]['tid']
    uname = t_info[tid]['username']
    if uname in t_uname_find:
        t_uname_find[uname].append(sid)
    else:
        t_uname_find[uname] = [sid]

# export dictionaries and scores as json files
with open('precomp_diff_clusters/precomp_16/s_name_find.json', 'w') as snf_file:
    json.dump(s_name_find, snf_file)
with open('precomp_diff_clusters/precomp_16/t_uname_find.json', 'w') as tuf_file:
    json.dump(t_uname_find, tuf_file)
with open('precomp_diff_clusters/precomp_16/s_info.json', 'w') as si_file:
    json.dump(s_info, si_file)
with open('precomp_diff_clusters/precomp_16/t_info.json', 'w') as ti_file:
    json.dump(t_info, ti_file)
with open('precomp_diff_clusters/precomp_16/candidates_scores.json', 'w') as cs_file:
    json.dump(candidates_scores, cs_file)

'''
# Justin Bieber
# twitter id
jb_tid = twitter.iloc[0,0]
# followers count
jb_count = twitter.iloc[0,5]
# manual count from following table
jb_fcount = 0
for i, row in following.iterrows():
    if row[1] == jb_tid:
        jb_fcount += 1
'''
