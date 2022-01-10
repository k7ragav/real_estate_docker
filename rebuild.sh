#!/bin/bash

WORKSPACE="$(dirname "$0")"
if [ "$WORKSPACE" = "." ]
then
  WORKSPACE="$(pwd)"
fi
DATE="$(date +%Y%m%d_%H%M%S)"
CONTAINERNAME="$(basename "$WORKSPACE")"
IMAGE="${CONTAINERNAME}_${DATE}"

# delete all older images, but leave latest one for backup
docker image ls "$CONTAINERNAME*" -q | tail -n +3 | parallel "docker image rm -f {}"

# add new file to always invalidate pip layer cache
touch "$DATE"

# build new image
docker build -t "$IMAGE" \
 "${WORKSPACE}" || exit 1

# remove file, we don't need it anymore
rm "$DATE"

# stop docker container
docker stop "$CONTAINERNAME" || true

# delete docker container
docker rm "$CONTAINERNAME" || true

# recreate and run docker container
docker run -itd --name "$CONTAINERNAME" "$IMAGE"
