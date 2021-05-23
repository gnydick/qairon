# syntax=docker/dockerfile:1
FROM alpine:3.13.5 AS BASE

RUN apk --no-cache add ca-certificates
RUN apk --no-cache add socat
RUN apk --no-cache add lvm2

RUN mkdir /tmp/pipe
WORKDIR /tmp/pipe
ADD start.sh ./
RUN mknod backpipe p

RUN chown -R nobody /tmp/pipe

USER nobody


