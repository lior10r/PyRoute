#/usr/bin/env sh

set -e
set -o pipefail

DOCKER_DIR="/mnt/shared/Installs/docker-ce-18.06"

# apt packages
DEB_DOCKER="$DOCKER_DIR/docker-ce_18.06.1~ce~3-0~ubuntu_amd64.deb"
DEB_SECCOMP="$DOCKER_DIR/libseccomp2_2.3.1-2.1ubuntu2~16.04.1_amd64.deb"

# apt installs
sudo apt install -y \
    $DEB_DOCKER \
    $DEB_SECCOMP \
    grub \
    python

# Add user to docker group
sudo adduser $(whoami) docker
sudo service docker restart
sleep 1

# Edit docker configuration
sudo /bin/bash -c 'cat > /etc/docker/daemon.json << EOF
{
    "insecure-registries" : ["jaro:1700"],
    "dns" : ["10.159.0.30", "10.159.0.50"],
    "iptables": false
}
EOF'
sudo service docker restart
sleep 1

# Needed for login (for this run only)
sudo chmod 777 /var/run/docker.sock

# Login to image repository
docker login -u masad -p masad jaro:1700

# Add network capabilities to python
sudo setcap cap_net_raw+ep $(grub-mkrelpath $(which python))

# Disable ip forwarding
sudo sysctl net.ipv4.ip_forward=0
