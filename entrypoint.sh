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

# ---

create_run_dir

# ---

python3 -u -m pyftpdlib -p $YDL_SERVER_PORT -d /tmp/$DOWNLOAD_DIR &
python3 -u $path/run/youtube-dl-server.py
