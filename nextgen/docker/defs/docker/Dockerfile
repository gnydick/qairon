FROM opensuse/leap:15.3

RUN zypper -n in docker

RUN zypper -n in jq \
 curl \
 git \
 bash

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscli-exe-linux-x86_64.zip
RUN zypper -n in zip \
    unzip
RUN unzip awscli-exe-linux-x86_64.zip

RUN ./aws/install

