FROM golang:1.15.2-alpine3.12 AS builder

RUN apk update && apk upgrade && \
    apk add --no-cache bash git

RUN go get github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb

FROM python:3.8

LABEL Description="Container generates json resources from jsonnet resources (grafana dashboards, prometheus rules)"

RUN mkdir /app
WORKDIR /app
ADD ./ /app/
RUN pip3 install .

RUN groupadd jsonnet-translator
RUN useradd --gid jsonnet-translator jsonnet-translator

COPY --from=builder /go/bin/jb /usr/local/bin/jb
COPY --from=builder /lib/* /lib/

RUN mkdir jsonnet_libs && cd jsonnet_libs && \
    jb init && \
    jb install https://github.com/grafana/grafonnet-lib/grafonnet@ff69572caf78c3163980d0d723c85a722eab73d9

RUN chmod -R 777 /app

ENV LIBSONNET_PATH=/app/jsonnet_libs

USER jsonnet-translator
