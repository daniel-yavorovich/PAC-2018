# Requirements

* Install [Docker](https://docs.docker.com/install/)

# Run client using docker

Please replace `/path/to/data` to your absolute path to data dir and execute:

    docker run --name=pac-2018 -d --restart=always -v /path/to/data:/usr/src/app/data yavorovych/pac-2018:client