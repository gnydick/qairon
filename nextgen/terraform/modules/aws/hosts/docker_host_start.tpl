#!/usr/bin/env bash


while [ ! -b /dev/xvdz ];
    do sleep 2
done



pgrep dockerd > /dev/null

if [ "$?" != 0 ]; then
    sudo /etc/init.d/docker start
    sleep 10
fi

RESULT="-1"

while [ "$RESULT" != "0" ];
   do sleep 2
   sudo /etc/init.d/docker start
   pgrep dockerd
   RESULT=$?
done

