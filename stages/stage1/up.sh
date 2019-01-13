#!/usr/bin/env sh

# docker-compose must be run from the same directory as docker-compose.yml
env=$(grub-mkrelpath $(dirname $0))

pushd $env > /dev/null
docker-compose up -d
popd > /dev/null
