FROM debian:buster-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-dev \
        python3-pip \
        python3-setuptools \
        gcc

COPY ./requirements.txt /src/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir toolz
RUN pip3 install --no-cache-dir -r /src/requirements.txt

RUN rm -rf ~/.cache/pip
