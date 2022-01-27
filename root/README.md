# Root

## Installation

    pip install -r requirements.txt

## Environment variable config

example:

    REDIS_SERVER_IP=localhost
    REDIS_SERVER_PORT=6379
    REDIS_SERVER_DB=0

* REDIS_SERVER_IP: ip of the server where redis is running
* REDIS_SERVER_PORT: port the redis is listening on
* REDIS_SERVER_DB: redis db. When launched from docker-compose set to 0

`.env` file is supported.

## Launch

    python ./main.py