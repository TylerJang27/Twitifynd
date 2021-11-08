# Twitifynd
CS 333: Algorithms in the real world final project

# Setup
1. This is currently configured to run Docker within an Ubuntu 20.04 host (vcm.duke.edu).
2. Follow instructions for installing stable [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) version
3. Follow instructions for installing stable [Docker Compose](https://docs.docker.com/compose/install/) on linux
4. Run `docker-compose build`
5. Run `docker-compose up --force-recreate`

See [init.sh] and [create.sh](db/create.sh) for current behavior and TODOs.

Steps 4-5 will need to be rerun on any code changes until hot deploy is configured.

To view current docker container information, run `docker ps` (may need to be run as `sudo`)