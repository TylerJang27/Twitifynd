from io import DEFAULT_BUFFER_SIZE
import json
import pandas as pd
import numpy as np

class Recommend:
    def __init__(self, artists_per_cluster):
        folder = 'precomp_diff_clusters/precomp_' + str(artists_per_cluster)
        with open(folder + '/s_info.json') as sif:
            self.s_info = json.load(sif)
        with open(folder + '/t_info.json') as tif:
            self.t_info = json.load(tif)
        with open(folder + '/candidates_scores.json') as csf:
            self.candidates_scores = json.load(csf)

    def get_recs(self, artists):
        all_recs = {}
        for artist in artists:
            all_recs[artist] = {'name': self.s_info[artist]['spotify name']}
            df_recs = pd.DataFrame(columns=['id', 'name', 'score'])
            for candidate in self.candidates_scores.get(artist):
                df_recs = df_recs.append({
                    'id': candidate[0],
                    'name': self.s_info[candidate[0]]['spotify name'],
                    'score': round(np.nan_to_num(candidate[1]), 3),
                    'link': "https://open.spotify.com/artist/" + candidate[0]}, ignore_index=True)
            df_recs.sort_values(by='score', ascending=True, inplace=True)
            df_recs.drop_duplicates(subset=['name'], inplace=True)
            df_recs.reset_index(drop=True, inplace=True)
            remove = []
            ptid = self.s_info[artist]['tid']
            for i, row in df_recs.iterrows():
                ctid = self.s_info[row[0]]['tid']
                if ptid in self.t_info:
                    if ctid in self.t_info[ptid]['following']:
                        remove.append(i)
            df_recs.drop(remove, inplace=True)
            all_recs[artist]['recs'] = df_recs.iloc[:, 1:]
        return all_recs
