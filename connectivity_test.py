import requests

def extract_twitter_id(spotify_id):
    r = requests.get('https://open.spotify.com/artist/{:}'.format(spotify_id))

    if r.status_code != 200:
        print("Unable to perform HTTP request for ID: {:}".format(spotify_id))
        return -1

    # {"name":"TWITTER","url":"https://twitter.com/justinbieber"}
    try:
        twitter_id = r.text.split('{"name":"TWITTER","url":"https://twitter.com/')[1].split('"')[0].split('?')[0]
    except IndexError:
        print("User has not connected their Spotify to Twitter")
        # FileWrapper.appendToFile(SPOTIFY_MISSING_TWITTER_FILE, "{:}".format(spotify_id))
        return -1

    return twitter_id

if __name__ == "__main__":
    extract_twitter_id('3TVXtAsR1Inumwj472S9r4')