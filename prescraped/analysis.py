import pandas as pd

df_artist_results = pd.read_csv("artist_result.csv")
header = ["id", "name", "genres", "followers", "popularity", "mean_danceability", "sd_danceability", "mean_energy", "sd_energy", "mean_key", "sd_key", "mean_loudness", "sd_loudness", "mean_mode", "sd_mode", "mean_speechiness", "sd_speechiness", "mean_acousticness", "sd_acousticness", "mean_instrumentalness", "sd_instrumentalness", "mean_liveness", "sd_liveness", "mean_valence", "sd_valence", "mean_tempo", "sd_tempo", "mean_duration_ms", "sd_duration_ms", "mean_time_signature", "sd_time_signature", "mean_chorus_hit", "sd_chorus_hit", "mean_sections", "sd_sections", "mean_target", "sd_target"]
df_artist_results.columns = header
print(df_artist_results.genres.str.len().max())
