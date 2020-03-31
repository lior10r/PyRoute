FROM ubuntu:16.04

RUN apt update

RUN apt install -y \
	util-linux \
	net-tools \
	iputils-ping \
    python3 \
    python3-pip \
    tcpdump \
    ssh \
    iperf

RUN python3 -m pip install -U pip

RUN python3 -m pip install \
	scapy \
	ipython

WORKDIR ~
