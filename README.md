# Twitifynd
CS 333: Algorithms in the real world final project

# Setup
1. This is currently configured to run Docker within an Ubuntu 20.04 host (vcm.duke.edu).
2. Follow instructions for installing stable [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) version
3. Follow instructions for installing stable [Docker Compose](https://docs.docker.com/compose/install/) on linux
4. Run `cp template.env .env` and add the necessary tokens.
5. Run `source .env`
6. Run `docker-compose build`
7. Run `docker-compose up --force-recreate`

See [init.sh] and [create.sh](db/create.sh) for current behavior and TODOs.

Steps 6-7 will need to be rerun on any code changes until hot deploy is configured.

To view current docker container information, run `docker ps` (may need to be run as `sudo`)

While the scripts are running/containers are live, you can view the current status of the database by running:
1. `docker inspect twitifynd_db_1 | grep IPAddress` to get the local IP of your db container.
2. `psql -h <IPAddress> -U postgres twitifynd`. The password can be found in the docker-compose file.