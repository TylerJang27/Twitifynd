CREATE TABLE testtable (id INT);
/* DO WE WANT OTHER NON-ARTIST TWITTER USERS? */
CREATE TABLE artist (
    id int NOT NULL PRIMARY KEY,
    artist_name varchar(32),
    twitter_id int NOT NULL,
    twitter_name varchar(25) NOT NULL, /* MAYBE EXTRACT INTO TWITTER_ARTIST */
    spotify_id varchar(25) NOT NULL,
    spotify_name varchar(25) NOT NULL /* MAYBE EXTRACT INTO SPOTIFY_ARTIST */
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
    follower_id int,
    followed_id int,
    PRIMARY KEY (follower_id, followed_id),
    FOREIGN KEY (follower_id) REFERENCES artist(twitter_id),
    FOREIGN KEY (followed_id) REFERENCES artist(twitter_id)
);

/* TODO: REPLACE WITH CLIENT-SIDE RATHER THAN SERVER SIDE COPY FUNCTION */
/* export code borrowed from https://stackoverflow.com/questions/17463299/export-postgres-database-into-csv-file */
CREATE OR REPLACE FUNCTION db_to_csv(path TEXT) RETURNS void AS $$
declare
   tables RECORD;
   statement TEXT;
begin
FOR tables IN 
   SELECT (table_name) AS schema_table
   FROM information_schema.tables t INNER JOIN information_schema.schemata s 
   ON s.schema_name = t.table_schema 
   WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
   AND t.table_type NOT IN ('VIEW')
   ORDER BY schema_table
LOOP
   statement := 'COPY ' || tables.schema_table || ' TO ''' || path || '/' || tables.schema_table || '.csv' ||''' DELIMITER '';'' CSV HEADER';
   EXECUTE statement;
END LOOP;
return;  
end;
$$ LANGUAGE plpgsql;