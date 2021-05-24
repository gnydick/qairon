FROM alpine



ENV KUBE_LATEST_VERSION="v1.10.0"

RUN apk add --update ca-certificates \
 && apk add --update -t deps jq \
 && apk add --update -t deps curl \
 && curl -L https://storage.googleapis.com/kubernetes-release/release/${KUBE_LATEST_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl \
 && chmod +x /usr/local/bin/kubectl \
 && rm /var/cache/apk/*
