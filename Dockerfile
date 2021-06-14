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



WORKDIR /opt/qairon
ADD requirements.txt /

RUN pip install -r /requirements.txt

ADD qairon/controllers /opt/qairon/controllers
ADD qairon/converters /opt/qairon/converters
ADD qairon/migrations /opt/qairon/migrations
ADD qairon/models /opt/qairon/models
ADD qairon/views /opt/qairon/views
ADD qairon/templates /opt/qairon/templates
ADD qairon/app.py /opt/qairon/
ADD qairon/base.py /opt/qairon/
ADD qairon/db.py /opt/qairon/
ADD qcli /opt/




RUN chown -R qairon_user:qairon_user /opt/qairon


USER qairon_user
RUN export SECRET_KEY=$SECRET_KEY
RUN export LC_ALL=$LC_ALL
RUN export LANG=$LANG
CMD gunicorn app:app -b 0.0.0.0:5001 --keep-alive 86400 --preload --workers=16 -k gevent
