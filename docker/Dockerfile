FROM golang:1.26-alpine AS go-builder
RUN apk update && apk upgrade && \
    apk add --no-cache bash git
RUN go install github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb@v0.6.0

FROM python:3.8 AS python-builder
RUN apt-get update && apt-get install -y wget
# gojsonnet (go-jsonnet >= 0.22) needs a modern Go toolchain to build from source;
# Debian's packaged golang-go is too old, so fetch an official Go release instead.
ARG GO_VERSION=1.26.5
RUN ARCH=$(dpkg --print-architecture) && \
    wget -q "https://go.dev/dl/go${GO_VERSION}.linux-${ARCH}.tar.gz" && \
    tar -C /usr/local -xzf "go${GO_VERSION}.linux-${ARCH}.tar.gz" && \
    rm "go${GO_VERSION}.linux-${ARCH}.tar.gz"
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:/usr/local/go/bin:$PATH"

RUN mkdir /app
ADD ./ /app
RUN pip3 install /app

FROM python:3.8-slim

LABEL Version="2.0.1"
LABEL Vendor="dNation"
LABEL Description="Container generates json resources from jsonnet resources (grafana dashboards, prometheus rules)"

RUN mkdir /app
WORKDIR /app
ADD ./ /app/

RUN groupadd kubernetes-jsonnet-translator && \
    useradd --gid kubernetes-jsonnet-translator kubernetes-jsonnet-translator

COPY --from=go-builder /go/bin/jb /usr/local/bin/jb
COPY --from=go-builder /lib/* /lib/
COPY --from=python-builder /opt/venv /opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && \
    mkdir jsonnet_libs && cd jsonnet_libs && \
    jb init && \
    jb install https://github.com/thelastpickle/grafonnet-polystat-panel@275a48de57afdac0d72219d82863d8ab8bd0e682 && \
    jb install https://github.com/grafana/grafonnet/gen/grafonnet-latest@41e6bfcbe4ef1054298ffff8664f1354c897dd2d

RUN chmod -R 777 /app

ENV LIBSONNET_PATH=/app/jsonnet_libs
ENV PATH="/opt/venv/bin:$PATH"

USER kubernetes-jsonnet-translator

CMD ["python","-u","translator/main.py"]
