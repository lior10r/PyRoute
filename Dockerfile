FROM jaro:1700/xenial

RUN apt install -y \
    python \
    python-scapy \
    ipython

WORKDIR ~
