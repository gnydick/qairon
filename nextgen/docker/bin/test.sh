#!/usr/bin/env bash

IMG=$1
VERFILE=""
VERPREFIX=""
if [[ "$2" != "" ]] ; then
    VERPREFIX=$2
    VERFILE=".$VERPREFIX-version"
else
    VERFILE=".version"
fi

echo "1) Current version: "$(cat defs/$IMG/$VERFILE)
echo "2) Update tag on current version"
echo "3) Upload other version..."
read  -n 1 -p "Choice: " choice
echo


if [ "$choice" == "1" ]; then
    echo
    cur_ver=$(cat defs/${IMG}/$VERFILE)
    echo    docker push $DOCKER_REGISTRY/$IMG:$cur_ver
    echo
fi

if [ "$choice" == "2" ]; then
    read -p "Version: " version
    echo

    if [[ "$2" != "" ]]; then
        TAG="$VERPREFIX-$version"
    else
        TAG=$version
    fi


    cur_ver=$(cat defs/${IMG}/$VERFILE)
    echo docker tag $DOCKER_REGISTRY/$IMG:$cur_ver $DOCKER_REGISTRY/$IMG:$TAG
    echo docker push $DOCKER_REGISTRY/$IMG:$TAG
    echo
fi

if [ "$choice" == "3" ]; then
    read -p "Version: " version
    echo
    echo docker push $DOCKER_REGISTRY/$IMG:$version
    echo
fi
