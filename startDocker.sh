#!/usr/bin/env bash
docker build -t xerohige/chimecho .
docker run --net="host" -v $(pwd):/server -p 8888:8888 -p 6006:6006 xerohige/chimecho sh -c "/server/startServer.sh"
