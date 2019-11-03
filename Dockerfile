FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8

LABEL maintainer "Daniel Wang <hello@danielwang.dev>"

RUN apk add --update --no-cache gcc make musl-dev libffi-dev openssl-dev g++

RUN pip install --upgrade pip
RUN pip install --no-binary pyNaCl cryptography
COPY requirements.txt /
RUN pip install --requirement /requirements.txt

COPY ./app /app

ENV LISTEN_PORT=8000
EXPOSE 8000
