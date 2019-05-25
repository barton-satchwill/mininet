# Mininet
FROM ubuntu:16.04

USER root

WORKDIR /root

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sudo \
    iproute2 \
    iputils-ping \
    net-tools \
    socat \
    tcpdump \
    vim \
    vlc \
    x11-xserver-utils \
    xterm \
    git-all \
    lsb-release

RUN git config --global url.https://github.com/.insteadOf git://github.com/
RUN git clone https://github.com/mininet/mininet

WORKDIR /root/mininet
RUN git checkout -b 2.2.2 2.2.2

WORKDIR /root
RUN chmod +x mininet/util/install.sh
RUN mininet/util/install.sh -a
