import json
import pandas as pd

class Recommend:
    def __init__(self):
        with open ('precomputed/artist_info.json') as aif:
            self.artist_info = json.load(aif)

        with open('precomputed/candidates_scores.json') as csf:
            self.candidates_scores = json.load(csf)
    def get_recs(self, artists):
        df_recs = pd.DataFrame(columns=['name', 'score', 'similar to'])
        for artist in artists:
            for candidate in self.candidates_scores.get(artist):
                df_recs = df_recs.append({
                    'name': self.artist_info[candidate[0]]['name'],
                    'score': candidate[1], 'similar to': self.artist_info[artist]['name']
                }, ignore_index=True)
        df_recs.sort_values(by='score', ascending=False, inplace=True)
        return df_recs.head()
