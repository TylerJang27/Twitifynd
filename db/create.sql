CREATE TABLE testtable (id INT);
CREATE TABLE artist (
    id int NOT NULL PRIMARY KEY,
    artist_name varchar(32),
    twitter_id int NOT NULL,
    twitter_name varchar(25) NOT NULL,
    spotify_id int NOT NULL,
    spotify_name varchar(25) NOT NULL,
);
CREATE TABLE twitter_artist(
    twitter_id int NOT NULL PRIMARY KEY,
    /* twitter public metrics and any other data we want to collect*/
    FOREIGN KEY (twitter_id) REFERENCES artist(twitter_id)
);
CREATE TABLE spotify_artist(
    spotify_id int NOT NULL PRIMARY KEY,
    /* spotify song attribute distribution */
    FOREIGN KEY (spotify_id) REFERENCES artist(spotify_id)
);
CREATE TABLE following(
    follower_id int FOREIGN KEY REFERENCES artist(twitter_id),
    followed_id int FOREIGN KEY REFERENCES artist(twitter_id)
);