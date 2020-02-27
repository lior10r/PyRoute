#!/bin/bash

docker-compose down

# Restore ICMP
sudo sysctl net.ipv4.icmp_echo_ignore_all=0
