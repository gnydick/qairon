FROM opensuse/leap:15.3

ENV HELM_VERSION="v3.5.4"
ENV KUBE_VERSION="v1.21.0"
ARG EXE_FILENAME=awscli-exe-linux-x86_64.zip


RUN zypper -n in \
    bash \
    curl \
    git \
    gzip \
    jq \
    tar \
    unzip \
    wget \
    which \
    zip


RUN curl -s -O https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz \
    && tar -xvf helm-${HELM_VERSION}-linux-amd64.tar.gz \
    && mv linux-amd64/helm /usr/local/bin \
    && rm -f /helm-${HELM_VERSION}-linux-amd64.tar.gz

RUN curl -s -L https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl


RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o $EXE_FILENAME \
    && unzip $EXE_FILENAME \
    && ./aws/install

RUN groupadd -r --gid 1000  helm \
    && useradd -r -m -s /bin/false -g helm helm --uid 1000

USER helm
WORKDIR /home/helm

RUN helm plugin install https://github.com/hypnoglow/helm-s3.git

RUN helm repo add bitnami https://charts.bitnami.com/bitnami
RUN helm repo update

RUN mkdir /home/helm/.aws
ADD aws_config /home/helm/.aws/config