import json
from numpy.lib.shape_base import apply_along_axis
import pandas as pd

class Recommend:
    def __init__(self):
        with open ('precomputed/artist_info.json') as aif:
            self.artist_info = json.load(aif)

        with open('precomputed/candidates_scores.json') as csf:
            self.candidates_scores = json.load(csf)
    def get_recs(self, artists):
        all_recs = {}
        for artist in artists:
            all_recs[artist] = {'name': self.artist_info[artist]['name']}
            df_recs = pd.DataFrame(columns=['name', 'score'])
            for candidate in self.candidates_scores.get(artist):
                df_recs = df_recs.append({
                    'name': self.artist_info[candidate[0]]['name'],
                    'score': candidate[1]
                }, ignore_index=True)
            df_recs.sort_values(by='score', ascending=False, inplace=True)
            all_recs[artist]['recs'] = df_recs.head()
        return all_recs

r = Recommend()
