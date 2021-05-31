FROM opensuse/leap:15.3

ENV HELM_VERSION="v3.5.4"
ENV KUBE_VERSION="v1.21.0"
ARG EXE_FILENAME=awscli-exe-linux-x86_64.zip


RUN zypper -n in jq \
 curl \
 git \
 bash

RUN zypper -n in tar \
    gzip

RUN zypper -n in wget

RUN curl -s -O https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN tar -xvf helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN mv linux-amd64/helm /usr/local/bin
RUN rm -f /helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN curl -s -L https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl
#RUN helm plugin install https://github.com/hypnoglow/helm-s3.git
#
RUN zypper -n in zip unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o $EXE_FILENAME
RUN unzip $EXE_FILENAME

RUN ./aws/install

RUN groupadd -r --gid 1000  helm && useradd -r -m -s /bin/false -g helm helm --uid 1000

RUN zypper -n in which

USER helm
WORKDIR /home/helm

RUN helm plugin install https://github.com/hypnoglow/helm-s3.git

RUN helm repo add bitnami https://charts.bitnami.com/bitnami
RUN helm repo update

RUN mkdir /home/helm/.aws
ADD aws_config /home/helm/.aws/config