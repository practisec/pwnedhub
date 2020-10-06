FROM python:3.7-alpine

ENV BUILD_DEPS="build-base gcc libc-dev libxslt-dev mariadb-dev"
ENV RUNTIME_DEPS="libxslt mariadb-connector-c-dev"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /pwnedhub

WORKDIR /pwnedhub

ADD ./REQUIREMENTS.txt /pwnedhub/REQUIREMENTS.txt

RUN apk update &&\
    apk add --no-cache $BUILD_DEPS $RUNTIME_DEPS &&\
    pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r REQUIREMENTS.txt &&\
    apk del $BUILD_DEPS &&\
    rm -rf /var/cache/apk/*
