FROM alpine:3.13.5

ENV HELM_VERSION="v3.5.4"
ENV KUBE_VERSION="v1.21.0"

RUN apk add --no-cache ca-certificates
RUN apk add --no-cache jq
RUN apk add --no-cache curl
RUN apk add --no-cache git
RUN apk add --no-cache bash

RUN curl -s -O https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN tar -xvf helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN mv linux-amd64/helm /usr/local/bin
RUN rm -f /helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN curl -s -L https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl
RUN helm plugin install https://github.com/hypnoglow/helm-s3.git

RUN addgroup --gid 1000 -S jenkins && adduser -s /bin/false -G jenkins -S jenkins --uid 1000

USER jenkins
WORKDIR /home/jenkins
RUN helm plugin install https://github.com/hypnoglow/helm-s3.git

RUN helm repo add bitnami https://charts.bitnami.com/bitnami
RUN helm repo update