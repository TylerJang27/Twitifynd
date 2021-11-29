import json
import pandas as pd
import numpy as np

class Recommend:
    def __init__(self):
        with open('precomputed/s_info.json') as sif:
            self.s_info = json.load(sif)
        with open('precomputed/t_info.json') as tif:
            self.t_info = json.load(tif)
        with open('precomputed/candidates_scores.json') as csf:
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
                    'score': round(np.nan_to_num(candidate[1]))}, ignore_index=True)
            df_recs.sort_values(by='score', ascending=False, inplace=True)
            df_recs.drop_duplicates(subset=['name'], inplace=True)
            all_recs[artist]['recs'] = df_recs.head()
        return all_recs
