#!/bin/bash

docker-compose up -d

# Disable ARP on ifaces
sudo ifconfig net1 -arp
sudo ifconfig net2 -arp

# Disable ICMP responses
sudo sysctl net.ipv4.icmp_echo_ignore_all=1
