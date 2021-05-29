FROM amazonlinux:2 as installer
ARG EXE_FILENAME=awscli-exe-linux-x86_64.zip



RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o $EXE_FILENAME
RUN yum update -y \
  && yum install -y unzip \
  && unzip $EXE_FILENAME \
  # The --bin-dir is specified so that we can copy the
  # entire bin directory from the installer stage into
  # into /usr/local/bin of the final stage without
  # accidentally copying over any other executables that
  # may be present in /usr/local/bin of the installer stage.
  && ./aws/install --bin-dir /aws-cli-bin/

FROM amazonlinux:2
ENV HELM_VERSION="v3.5.4"
ENV KUBE_VERSION="v1.21.0"

RUN yum update -y \
  && yum install -y less groff tar file \
  && yum clean all
COPY --from=installer /usr/local/aws-cli/ /usr/local/aws-cli/
COPY --from=installer /aws-cli-bin/ /usr/local/bin/


RUN curl -s -O https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN tar -xvf helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN mv linux-amd64/helm /usr/local/bin
RUN rm -f /helm-${HELM_VERSION}-linux-amd64.tar.gz
RUN curl -s -L https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl
RUN helm plugin install https://github.com/hypnoglow/helm-s3.git
#ADD kubectl /usr/local/bin/kubectl
#RUN chmod +x /usr/local/bin/kubectl

