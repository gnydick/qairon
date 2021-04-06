#!/usr/bin/env bash


while [ ! -b /dev/xvdz ];
    do sleep 2
done


# pvscan | grep docker
#
# if [ "$?" == 0 ]; then
#     vgimport -f docker
# fi
#
#
# while [ ! -b /dev/xvds ];
#     do sleep 2
# done
#
# mkdir -p /mnt/state/
#
#
# mount /dev/xvds /mnt/state
#
# if [ "$?" != "0" ]; then
#     mkfs.xfs -f /dev/xvds
#     mount /dev/xvds /mnt/state -t xfs 2>&1 > /dev/null
#     if [ "$?" != "0" ]; then
#         echo "State file system failed"
#         exit 255
#     fi
# fi


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

# $(aws ecr get-login --region "${region}" | sed 's/-e none//') # needed for AWS registry
sudo docker run -d --restart=unless-stopped -p 80:80 -p 443:443 \
    --name rancher-server -v /mnt/state:/var/lib/rancher  rancher/rancher:v2.0.6
