#!/bin/bash


IMG=$1
VER=$2
DFILE="Dockerfile" && [[ "$3" != "" ]] && DFILE=$3
TAG=""
VERFILE=""

if [[ "$4" != "" ]]; then
    TAG=$4-$VER
    VERFILE=".$4-version"
else
    TAG=$VER
    VERFILE=".version"
fi



if [ -z "$VER" ]; then
    echo "Need new version."
    echo "Current version is " $(cat defs/$IMG/$VERFILE)
    exit 255
fi




docker build --network host -t $DOCKER_REGISTRY/$IMG:$TAG defs/$IMG -f defs/$IMG/$DFILE  && echo $VER > defs/$IMG/$VERFILE
