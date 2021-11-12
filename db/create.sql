CREATE TABLE testtable (id INT); /* TODO: REMOVE */
CREATE TABLE artist (
    id int NOT NULL PRIMARY KEY,
    artist_name varchar(50), /* should we scrap this in favor of the spotify name? */
    twitter_id int NULL, /* I was thinking we may have spotify or twitter users without being linked to start with, so it may be useful to keep this structure */
    spotify_id char(22) NULL,
    FOREIGN KEY (twitter_id) REFERENCES twitter_user(twitter_id),
    FOREIGN KEY (spotify_id) REFERENCES spotify_artist(spotify_id)
);
CREATE TABLE twitter_user(
    twitter_id int NOT NULL PRIMARY KEY,
    twitter_username varchar(50) NOT NULL,
    twitter_name varchar(50) NOT NULL,
    bio varchar(160) NOT NULL,
    verified boolean NOT NULL,
    protected boolean NOT NULL,
    followers_count INT NOT NULL,
    following_count INT NOT NULL,
    tweet_count INT NOT NULL,
    listed_count INT NOT NULL
);
CREATE TABLE following(
    follower_id int,
    followed_id int,
    PRIMARY KEY (follower_id, followed_id),
    FOREIGN KEY (follower_id) REFERENCES twitter_user(twitter_id),
    FOREIGN KEY (followed_id) REFERENCES twitter_user(twitter_id)
);
CREATE TABLE spotify_artist(
    spotify_id char(22) NOT NULL PRIMARY KEY,
    spotify_name varchar(50) NOT NULL,
    genres varchar(64), /* should we make this a many-one separate table or an index or something? */
    followers INT NOT NULL,
    popularity INT NOT NULL,
    mean_danceability FLOAT NOT NULL,
    sd_danceability FLOAT NOT NULL,
    mean_energy FLOAT NOT NULL,
    sd_energy FLOAT NOT NULL,
    mean_key FLOAT NOT NULL,
    sd_key FLOAT NOT NULL,
    mean_loudness FLOAT NOT NULL,
    sd_loudness FLOAT NOT NULL,
    mean_mode FLOAT NOT NULL,
    sd_mode FLOAT NOT NULL,
    mean_speechiness FLOAT NOT NULL,
    sd_speechiness FLOAT NOT NULL,
    mean_acousticness FLOAT NOT NULL,
    sd_acousticness FLOAT NOT NULL,
    mean_instrumentalness FLOAT NOT NULL,
    sd_instrumentalness FLOAT NOT NULL,
    mean_liveness FLOAT NOT NULL,
    sd_liveness FLOAT NOT NULL,
    mean_valence FLOAT NOT NULL,
    sd_valence FLOAT NOT NULL,
    mean_tempo FLOAT NOT NULL,
    sd_tempo FLOAT NOT NULL,
    mean_duration_ms FLOAT NOT NULL,
    sd_duration_ms FLOAT NOT NULL,
    mean_time_signature FLOAT NOT NULL,
    sd_time_signature FLOAT NOT NULL,
    mean_chorus_hit FLOAT NOT NULL,
    sd_chorus_hit FLOAT NOT NULL,
    mean_sections FLOAT NOT NULL,
    sd_sections FLOAT NOT NULL,
    mean_target FLOAT NOT NULL,
    sd_target FLOAT NOT NULL
);