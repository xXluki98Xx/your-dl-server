#!/bin/bash
set -e

# ---

create_run_dir() {
	mkdir -p /usr/src/app/run
	chmod 775 /usr/src/app/run
	cp -r /usr/src/app/config /usr/src/app/run
}

create_download_dir() {
	mkdir -p /tmp/yt-downloads
	chmod 775 /tmp/yt-downloads
}

# ---

create_run_dir
create_download_dir

# ---

python3 -u run/youtube-dl-server.py
