CREATE TABLE testtable (id INT); /* TODO: REMOVE */
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
    follower_id int NOT NULL,
    followed_id int NOT NULL,
    PRIMARY KEY (follower_id, followed_id),
    FOREIGN KEY (follower_id) REFERENCES twitter_user(twitter_id),
    FOREIGN KEY (followed_id) REFERENCES twitter_user(twitter_id)
);
CREATE TABLE spotify_artist(
    spotify_id char(22) NOT NULL PRIMARY KEY,
    spotify_name varchar(50) NOT NULL,
    genres varchar(320), /* should we make this a many-one separate table or an index or something? */
    followers FLOAT NOT NULL,
    popularity INT NOT NULL,
    mean_danceability FLOAT NULL,
    sd_danceability FLOAT NULL,
    mean_energy FLOAT NULL,
    sd_energy FLOAT NULL,
    mean_key FLOAT NULL,
    sd_key FLOAT NULL,
    mean_loudness FLOAT NULL,
    sd_loudness FLOAT NULL,
    mean_mode FLOAT NULL,
    sd_mode FLOAT NULL,
    mean_speechiness FLOAT NULL,
    sd_speechiness FLOAT NULL,
    mean_acousticness FLOAT NULL,
    sd_acousticness FLOAT NULL,
    mean_instrumentalness FLOAT NULL,
    sd_instrumentalness FLOAT NULL,
    mean_liveness FLOAT NULL,
    sd_liveness FLOAT NULL,
    mean_valence FLOAT NULL,
    sd_valence FLOAT NULL,
    mean_tempo FLOAT NULL,
    sd_tempo FLOAT NULL,
    mean_duration_ms FLOAT NULL,
    sd_duration_ms FLOAT NULL,
    mean_time_signature FLOAT NULL,
    sd_time_signature FLOAT NULL,
    mean_chorus_hit FLOAT NULL,
    sd_chorus_hit FLOAT NULL,
    mean_sections FLOAT NULL,
    sd_sections FLOAT NULL,
    mean_target FLOAT NULL,
    sd_target FLOAT NULL
);
CREATE TABLE artist (
    id int NOT NULL PRIMARY KEY,
    twitter_id int NULL, /* I was thinking we may have spotify or twitter users without being linked to start with, so it may be useful to keep this structure */
    spotify_id char(22) NULL,
    FOREIGN KEY (twitter_id) REFERENCES twitter_user(twitter_id),
    FOREIGN KEY (spotify_id) REFERENCES spotify_artist(spotify_id)
);