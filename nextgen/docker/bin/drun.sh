#!/usr/bin/env bash

IMG=$1
TAG=$2
SHELL=$3

docker run -it --entrypoint=$SHELL $DOCKER_REGISTRY/$IMG:$TAG
