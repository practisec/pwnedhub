FROM python:3.7-alpine

RUN mkdir -p /pwnedhub

WORKDIR /pwnedhub

ADD ./REQUIREMENTS.txt /pwnedhub/REQUIREMENTS.txt

RUN apk add --no-cache --virtual .build-deps build-base gcc libc-dev libxslt-dev mariadb-dev &&\
    apk add --no-cache libxslt mariadb-connector-c-dev &&\
    pip install --no-cache-dir -r REQUIREMENTS.txt &&\
    apk del .build-deps
