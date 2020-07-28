#!/bin/bash
set -e

# ---

path="/usr/src/youtube-dl-server"

# ---

create_run_dir() {
	mkdir -p $path/run && chmod 775 $path/run
	if [ -z "$(ls -A $path/run)" ]; then
		cp -r $path/config/* $path/run/
	fi
}

create_download_dir() {
	mkdir -p /tmp/yt-downloads
	chmod 775 /tmp/yt-downloads
}

# ---

create_run_dir
create_download_dir

# ---

python3 -u $path/run/youtube-dl-server.py
