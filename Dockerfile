FROM python:3.9.2

ENV FLASK_APP=app.py
#ENV SECRET_KEY=12345 this needs to be baked in
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ARG version

ENV VERSION $version

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install apt-utils && \
    apt-get -y install python3 && \
    apt-get -y install python3-pip && \
    apt-get -y install python3-gevent && \
    apt-get -y clean

RUN useradd -m -d /opt/qairon qairon_user



WORKDIR /opt/qairon/qairon
ADD requirements.txt /

RUN pip install -r /requirements.txt

ADD controllers /opt/qairon/controllers
ADD converters /opt/qairon/converters
ADD migrations /opt/qairon/migrations
ADD models /opt/qairon/models
ADD views /opt/qairon/views
ADD templates /opt/qairon/templates
ADD serializers /opt/qairon/serializers
ADD static /opt/qairon/static
ADD plugins /opt/qairon/plugins
ADD app.py /opt/qairon
ADD base.py /opt/qairon
ADD db.py /opt/qairon
ADD qairon_cli/qcli /opt/qairon




RUN mkdir /opt/config
RUN chown -R qairon_user:qairon_user /opt/qairon /opt/config


USER qairon_user
RUN export SECRET_KEY=$SECRET_KEY
RUN export LC_ALL=$LC_ALL
RUN export LANG=$LANG

WORKDIR /opt/qairon
RUN echo $version > .version


