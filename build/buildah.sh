#!/usr/bin/env bash

set -o errexit

# Create a container
container=$(buildah from emmercm/libtorrent)

# Labels
buildah config --label maintainer="lRamm <lukas.ramm.1998@gmail.com>" $container

# ---

# Installing Software
buildah run $container -- apk add --no-cache --update bash ffmpeg tzdata axel git curl
buildah run $container -- mkdir -p /usr/src/youtube-dl-server
buildah run $container -- git clone https://github.com/xXluki98Xx/youtube-dl-server.git /usr/src/youtube-dl-server
#buildah run $container -- bash -c "cd /usr/src/youtube-dl-server && git checkout feature"
buildah run $container -- pip3 install --upgrade pip --no-cache-dir -r /usr/src/youtube-dl-server/build/requirements.txt
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

buildah commit --format docker $container youtube-dl-server
#buildah commit --format docker $container ydl-feature
