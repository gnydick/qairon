FROM python:3.9.2

ENV FLASK_APP=app.py
ENV SECRET_KEY=12345
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

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

ADD qairon/controllers /opt/qairon/qairon/controllers
ADD qairon/converters /opt/qairon/qairon/converters
ADD qairon/migrations /opt/qairon/qairon/migrations
ADD qairon/models /opt/qairon/qairon/models
ADD qairon/views /opt/qairon/qairon/views
ADD qairon/templates /opt/qairon/qairon/templates
ADD qairon/app.py /opt/qairon/qairon
ADD qairon/base.py /opt/qairon/qairon
ADD qairon/db.py /opt/qairon/qairon
ADD qcli /opt/qairon




RUN chown -R qairon_user:qairon_user /opt/qairon


USER qairon_user
RUN export SECRET_KEY=$SECRET_KEY
RUN export LC_ALL=$LC_ALL
RUN export LANG=$LANG
WORKDIR /opt/qairon
CMD gunicorn qairon.app:app -b 0.0.0.0:5001 --keep-alive 86400 --preload --workers=16 -k gevent
