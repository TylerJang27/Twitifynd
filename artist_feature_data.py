import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from collections import defaultdict
import statistics

client_id = '0427be66657647dfa34c33a8f77740be'
client_secret = '178c632f057948fba89f7c72e1d946e3'

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#  get user's top artists
#   - current_user_top_artists(limit=20, offset=0, time_range='medium_term')
#  loop through top artists
#  get their top tracks
#  - artist_top_tracks(artist_id, country='US')
#  get audio features for each of that artists tracks
#  - audio_features(tracks=[])
#  average and find standard deviation

# print(sp.current_user())

# Olivia Rodrigo: '1McMsnEElThX1knmY4oliG'
# Pitbull: '0TnOYISbd1XYRBk9myaseg'
# Adele: '4dpARuHxo51G3z768sgnrY'
# Travis Scott: '0Y5tJX1MQlPlqiwlOH1tJY'
artist_id = '0TnOYISbd1XYRBk9myaseg'

def getTrackIDs(artist_id):
    ids = []
    playlist = sp.artist_top_tracks(artist_id, country = 'US')
    # sp.user_playlist(user, playlist_id)
    
    for item in playlist['tracks']:
      #  track = item['track']
      ids.append(item['id'])
    return ids

ids = getTrackIDs(artist_id)

def getTrackFeatures(id):
    meta = sp.track(id)
    features = sp.audio_features(id)

    # meta
    # name = meta['name']
    # album = meta['album']['name']
    # artist = meta['album']['artists'][0]['name']
    # release_date = meta['album']['release_date']
    # length = meta['duration_ms']
    popularity = meta['popularity']

    # features
    acousticness = features[0]['acousticness']
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    loudness = features[0]['loudness']
    speechiness = features[0]['speechiness']
    tempo = features[0]['tempo']
    # time_signature = features[0]['time_signature']

    track = [
        popularity, danceability,
        acousticness, energy, instrumentalness, liveness,
        loudness, speechiness, tempo
    ]

    return track


tracks = []

for i in range(len(ids)):
    time.sleep(.5)
    track = getTrackFeatures(ids[i])
    tracks.append(track)

featureDict = defaultdict(list)
features = ["popularity", "danceability", "acousticness","energy",
 "instrumentalness","liveness", "loudness", "speechiness", "tempo"]

for i in range(len(tracks)):
  for j in range(len(tracks[0])):
    featureDict[features[j]].append(float(tracks[i][j]))

      
def avg(feature):
    return sum(feature)/len(feature)

avgDict = {}

for key, value in featureDict.items():
  avgDict[key] = avg(value)

stdDict = {}

for key, value in featureDict.items():
  stdDict[key] = statistics.stdev(value)

resultDict = defaultdict(list)

for i in (avgDict, stdDict):
    for key, value in i.items():
        resultDict[key].append(value)

df = pd.DataFrame.from_dict(resultDict, orient='index', columns = ['average', 'standard deviation'])

print("For " + sp.artist(artist_id).get('name') + "'s Top Tracks:")
print(df)