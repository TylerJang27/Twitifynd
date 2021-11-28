import os
import pandas as pd


if __name__ == "__main__":
    out_string = ""
    f = open("prescraped/missing_twitter.txt", "r")
    full_string = f.read()

    header = ["id", "name", "genres", "followers", "popularity", "mean_danceability", "sd_danceability", "mean_energy", "sd_energy", "mean_key", "sd_key", "mean_loudness", "sd_loudness", "mean_mode", "sd_mode", "mean_speechiness", "sd_speechiness", "mean_acousticness", "sd_acousticness", "mean_instrumentalness", "sd_instrumentalness", "mean_liveness", "sd_liveness", "mean_valence", "sd_valence", "mean_tempo", "sd_tempo", "mean_duration_ms", "sd_duration_ms", "mean_time_signature", "sd_time_signature", "mean_chorus_hit", "sd_chorus_hit", "mean_sections", "sd_sections", "mean_target", "sd_target"]

    df = pd.read_csv("prescraped/artist_result.csv", header=None)
    df.columns = header
    artist_names = pd.Series(df["name"]).unique()
    # print("La Sonora Santanera" in artist_names)

    while len(full_string) > 0:
        cut_id = full_string[0:22]
        full_string = full_string[22:]
        cut_artist = ""
        if len(full_string) > 0 and full_string[0] == ",":
            full_string = full_string[1:]
            count = 40
            while True:
                cut_artist = full_string[0:count]
                if cut_artist in artist_names:
                    full_string = full_string[count:]
                    break
                count -= 1
                if count == 0:
                    print(count, cut_artist)
                if count > 50:
                    break
        else:
            cut_artist = df.loc[df['id'] == cut_id]['name'].values[0]
            # TODO: ATTEMPT TO EXTRACT TWITTER ID THROUGH API QUERY
        new_row = cut_id + "," + cut_artist + "," + "\n"
        if new_row not in out_string:
            out_string += new_row

    out_f = open("prescraped/missing_twitter_fixed.txt", "w")
    out_f.write(out_string)
    out_f.close()



    