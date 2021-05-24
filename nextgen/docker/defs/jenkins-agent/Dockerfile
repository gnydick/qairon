FROM jenkins/jnlp-slave:3.29-1
USER root
RUN groupadd -g 995 docker
RUN usermod -a -G docker jenkins
ENV DOCKERVERSION=17.09.1-ce
RUN curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKERVERSION}.tgz \
  && tar xzvf docker-${DOCKERVERSION}.tgz --strip 1 \
                 -C /usr/local/bin docker/docker \
  && rm docker-${DOCKERVERSION}.tgz

RUN apt-get update
RUN apt-get install -y coreutils groovy awscli jq
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*



RUN mkdir -p /home/jenkins/.ssh
ADD .ssh/* /home/jenkins/.ssh/
RUN chmod  0600 /home/jenkins/.ssh/*
RUN chown -R jenkins /home/jenkins/.ssh
USER jenkins
WORKDIR /home/jenkins



