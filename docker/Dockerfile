#
# Copyright 2020 The dNation Jsonnet Translator Authors. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

FROM golang:1.15.2-alpine3.12 AS go-builder
RUN apk update && apk upgrade && \
    apk add --no-cache bash git
RUN go get github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb

FROM python:3.8 AS python-builder
RUN apt-get update

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir /app
ADD ./ /app
RUN pip3 install /app

FROM python:3.8-slim

LABEL Version="0.3.0"
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

RUN mkdir jsonnet_libs && cd jsonnet_libs && \
    jb init && \
    jb install https://github.com/grafana/grafonnet-lib/grafonnet@daad85cf3fad3580e58029414630e29956aefe21

RUN chmod -R 777 /app

ENV LIBSONNET_PATH=/app/jsonnet_libs
ENV PATH="/opt/venv/bin:$PATH"

USER kubernetes-jsonnet-translator

CMD ["python","-u","translator/main.py"]
