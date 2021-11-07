#!/usr/bin/env bash

set -o errexit

# Create a container
# container=$(buildah from jrottenberg/ffmpeg:4.0-nvidia)
container=$(buildah from python:slim)

# Labels
buildah config --label maintainer="lRamm <lukas.ramm.1998@gmail.com>" $container

# ---

# Installing Software
buildah run $container -- sh -c 'apt update && apt upgrade -y && apt install -y git'

buildah run $container -- git clone https://github.com/xXluki98Xx/your-dl-server.git /app/your-dl-server

buildah run $container -- pip3 install --no-cache-dir -r /app/your-dl-server/requirements.txt --upgrade
buildah run $container -- sh -c 'cat /app/your-dl-server/requirements-apt.txt | xargs apt install -y'

buildah run $container -- rm -rf \
                            /var/lib/apt/lists/* \
                            /var/tmp/*

buildah commit $container

# ---

# Config Container
buildah config \
	--healthcheck-timeout 2s \
	--healthcheck-retries 3 \
	--healthcheck-interval 10s \
	--healthcheck-start-period 30s \
	--healthcheck "curl http://0.0.0.0:8080 || exit 1" \
	--workingdir /app/your-dl-server \
	--cmd ./entrypoint.sh \
	--port 8080/tcp \
	$container

buildah commit --format docker $container your-dl-server
#buildah commit --format docker $container ydl-feature
