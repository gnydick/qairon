#!/bin/sh

socat TCP4-LISTEN:$1,fork,reuseaddr TCP4:$2:$3