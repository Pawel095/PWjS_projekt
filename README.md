# Node 

## Installation

    pip install -r requirements.txt

or

    poetry install

## Config

example:

    ROOT_SERVER_IP=192.168.2.1
    ROOT_SERVER_PORT=6379
    ROOT_SERVER_DB=0
    NODE_NAME=pawel-main
    NODE_PREFIX=NODE

* ROOT_SERVER_IP: ip of the server where redis is running
* ROOT_SERVER_PORT: port the redis is listening on
* ROOT_SERVER_DB: redis db. When launched from docker-compose set to 0

* NODE_NAME: name of the node. will be used with prefix to construct the id.
* NODE_PREFIX: prefix added to node name.
  * Node id is as follows: `NODE_NAME-NODE_PREFIX`. in the example above node id is `NODE-pawel-main`

`.env` file is supported.

## Building

    pyinstaller main.spec

The executable will be built in `dist` folder.

## Special considerations

1. CPU temp is really buggy in windows.