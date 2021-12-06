# Twitifynd
CS 333: Algorithms in the real world final project

# Setup
1. This is currently configured to run Docker within an Ubuntu 20.04 host (vcm.duke.edu).
2. Follow instructions for installing stable [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) version
3. Follow instructions for installing stable [Docker Compose](https://docs.docker.com/compose/install/) on linux
4. Run `cp template.env .env` and add the necessary tokens.
5. Run `source .env`
6. Run `sudo docker-compose up --build`

See [init.sh] and [create.sh](db/create.sh) for current behavior and TODOs.

Steps 6-7 will need to be rerun on any code changes until hot deploy is configured.

# Analysis
To view current docker container information, run `docker ps` (may need to be run as `sudo`)

While the scripts are running/containers are live, you can view the current status of the database by running:
1. `docker inspect twitifynd_db_1 | grep IPAddress` to get the local IP of your db container.
2. `psql -h <IPAddress> -U postgres twitifynd`. The password can be found in the docker-compose file.

# Loading Data
1. (ON YOUR COMPUTER) Download the files from my email and unzip them
2. (ON YOUR COMPUTER) `scp -r ~/Downloads/log_2021-11-29_00:37:16 vcm@vcm_url:~/log_2021-11-29_00:37:16` (replace the first part with wherever you downloaded it to and the second part with the name of your vcm hostname. You may find it helpful to make a Documents directory at the destination rather than just putting it in home (~))
3. (ON YOUR VM) `sudo cp -r ~/log_2021-11-29_00:37:16 /var/lib/docker/volumes/twitifynd_script_data/_data/log_2021-11-29_00:37:16` (requires you to have run the docker stuff at least once for that directory to exist)
4. (ON YOUR VM) Go to [docker-compose.yml](docker-compose.yml) and make sure DB_PROCESS on line 29 is set to 2 (this forces it to load from csv’s that we just pasted)
5. (ON YOUR VM) Run `sudo docker-compose up --build twitifynd`

# Architecture Overview
This repository is set up using [docker-compose.yml](docker-compose.yml). This file outlines how the different containers are configured. At the time of writing, there are 2 standard images (a mail server (unauthenticated) and a postgresql server) and 1 custom container. This is specified in the [Dockerfile](Dockerfile).

There are different options for running the latter, which has an entrypoint in [init.sh](init.sh). Depending on the configuration, it will make sure the database is up, the tables have been created, and the necessary data is loaded from backups before proceeding to scrape data for spotify and twitter analysis.