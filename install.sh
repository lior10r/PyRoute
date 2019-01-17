#/usr/bin/env sh

set -e
set -o pipefail

installs="/mnt/shared/Installs"
libsec="$installs/docker-ce-18.06/libseccomp2_2.3.1-2.1ubuntu2~16.04.1_amd64.deb"
docker="$installs/docker-ce-18.06/docker-ce_18.06.1~ce~3-0~ubuntu_amd64.deb"
docker_compose="$installs/docker-compose/docker-compose"

# apt installs
sudo apt install -y \
    $docker \
    $libsec \
    grub \
    python

sudo pip install \
    scapy

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

# Install docker-compose
sudo cp $docker_compose /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
