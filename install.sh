#/usr/bin/env sh

set -e
set -o pipefail

docker_compose="/mnt/shared/Installs/docker-compose/1.24.1/docker-compose"

# Allow python to send packets as non-sudo
sudo setcap cap_net_admin,cap_net_raw+eip /usr/bin/python3.5

if [ ! -f $docker_compose ]; then
  echo "Cannot locate $docker_compose. Possibly due to missing mount of //mtzfilesrv/shared."
  echo
  echo "When having such mount point, please run:"
  echo "    sudo cp -v $docker_compose /usr/local/bin/docker-compose"
  echo "    sudo chmod +x /usr/local/bin/docker-compose"
else
  sudo cp -v $docker_compose /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
fi
