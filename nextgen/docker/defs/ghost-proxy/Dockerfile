# syntax=docker/dockerfile:1
FROM alpine:3.13.5 AS BASE

RUN apk --no-cache add ca-certificates
RUN apk --no-cache add socat

ADD start.sh ./
USER nobody


