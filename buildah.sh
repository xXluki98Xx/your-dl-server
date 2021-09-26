#!/usr/bin/env bash

set -o errexit

# Create a container
container=$(buildah from debian:stable-slim)

# Labels
buildah config --label maintainer="lRamm <lukas.ramm.1998@gmail.com>" $container

# ---

# Installing Software
buildah run $container -- apt update
buildah run $container -- apt upgrade
buildah run $container -- apt install -y python3 python3-pip git

buildah run $container -- git clone https://github.com/xXluki98Xx/youtube-dl-server.git /app/youtube-dl-server
buildah run $container -- cd /app/youtube-dl-server/ && git checkout refactoring
buildah run $container -- /app/your-dl-server/docs/debian-install.sh

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
	--workingdir /usr/src/youtube-dl-server \
	--cmd ./entrypoint.sh \
	--port 8080/tcp \
	$container

buildah commit --format docker $container your-dl-server
#buildah commit --format docker $container ydl-feature
