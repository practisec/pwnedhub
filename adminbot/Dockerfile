FROM python:3.10-alpine

ENV BUILD_DEPS=""
ENV RUNTIME_DEPS="firefox"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /src

WORKDIR /src

ADD ./REQUIREMENTS.txt /src/REQUIREMENTS.txt

RUN apk update &&\
    apk add --no-cache $BUILD_DEPS $RUNTIME_DEPS &&\
    pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r REQUIREMENTS.txt &&\
    apk del $BUILD_DEPS &&\
    rm -rf /var/cache/apk/*
