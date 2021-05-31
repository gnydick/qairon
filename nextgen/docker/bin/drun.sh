#!/usr/bin/env bash
DOCKER_REGISTRY=${_account}.dkr.ecr.${_region}.amazonaws.com

IMG=$1
TAG=$2
SHELL=$3

docker run -it -u root --entrypoint=$SHELL $DOCKER_REGISTRY/$IMG:$TAG
