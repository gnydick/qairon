#!/bin/sh

nc -lk -p $1 0<backpipe | nc -v $2 $3 | tee backpipe
socat TCP4-LISTEN:$1,fork,reuseaddr TCP4:$2:$3