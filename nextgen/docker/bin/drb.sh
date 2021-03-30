#!/usr/bin/env bash

IMG=$1


docker build -t $DOCKER_REGISTRY/$IMG:$(cat defs/$IMG/.version) defs/$IMG