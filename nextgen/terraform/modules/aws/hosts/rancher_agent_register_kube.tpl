#!/usr/bin/env bash


while [ ! -b /dev/xvdz ];
    do sleep 2
done



while [ ! -b /dev/xvds ];
    do sleep 2
done

mkdir -p /mnt/state/


mount /dev/xvds /mnt/state

if [ "$?" != "0" ]; then
    mkfs.xfs -f /dev/xvds
    mount /dev/xvds /mnt/state -t xfs 2>&1 > /dev/null
    if [ "$?" != "0" ]; then
        echo "State file system failed"
        exit 255
    fi
fi


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

sudo docker run -d --privileged --restart=unless-stopped --net=host -v /etc/kubernetes:/etc/kubernetes -v /var/run:/var/run   rancher/rancher-agent:v2.0.6 --server https://rancher0.rancher.prod.us-west-2.priv:443 --token ${token} --ca-checksum ${checksum} --${kube_role}


