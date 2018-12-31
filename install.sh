#/usr/bin/env sh

set -e
set -o pipefail

DOCKER_DIR="/mnt/shared/Installs/docker-ce-18.06"
DOCKER_DEB="./docker-ce_18.06.1~ce~3-0~ubuntu_amd64.deb"
DOCKER_LIB="./libseccomp2_2.3.1-2.1ubuntu2~16.04.1_amd64.deb"

function title
{
    local GREEN="\033[1;32m"
    local NORMAL="\033[0m"

    echo -e $GREEN${1}$NORMAL
}

# Install dependencies
sudo apt install -y grub python

# Add network capabilities to python
sudo setcap cap_net_raw+ep $(grub-mkrelpath $(which python))

# Disable ip forwarding
sudo sysctl net.ipv4.ip_forward=0

# Install docker
pushd $DOCKER_DIR
sudo apt-get install -y $DOCKER_DEB $DOCKER_LIB
popd

sudo adduser $(whoami) docker
sudo service docker stop
sudo service docker start
sleep 1

# Configure docker
sudo /bin/bash -c 'cat > /etc/docker/daemon.json << EOF
{
    "insecure-registries" : ["jaro:1700"],
    "dns" : ["10.159.0.30", "10.159.0.50"],
    "iptables": false
}
EOF'
sudo service docker restart
sleep 1

# For this run only
sudo chmod 777 /var/run/docker.sock

# Logic to inage repository
docker login -u masad -p masad jaro:1700
