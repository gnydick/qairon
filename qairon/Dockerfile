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

ADD controllers /opt/qairon/controllers
ADD converters /opt/qairon/converters
ADD migrations /opt/qairon/migrations
ADD models /opt/qairon/models
ADD views /opt/qairon/views
ADD app.py /opt/qairon/
ADD base.py /opt/qairon/
ADD db.py /opt/qairon/
ADD qcli /opt/qairon/


ADD templates /opt/qairon/templates

RUN chown -R qairon_user:qairon_user /opt/qairon


USER qairon_user
RUN export SECRET_KEY=$SECRET_KEY
RUN export LC_ALL=$LC_ALL
RUN export LANG=$LANG
CMD gunicorn app:app -b 0.0.0.0:5001 --keep-alive 86400 --preload --workers=16 -k gevent
