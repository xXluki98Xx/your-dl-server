[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://raw.githubusercontent.com/manbearwiz/youtube-dl-server/master/LICENSE)

# your-dl-server

This project is a Branch/ Fork of the original work of [manbearwiz](https://github.com/manbearwiz/youtube-dl-server).

Original Work: Very spartan Web and REST interface for downloading youtube videos onto a server. [`bottle`](https://github.com/bottlepy/bottle) + [`youtube-dl`](https://github.com/rg3/youtube-dl).

---

Bugs:

  - 

Features:

  - Improvement Threads: work of [nachtjasmin](https://github.com/nachtjasmin/youtube-dl-server/blob/master/youtube-dl-server.py)
  - Fileserver: work of [bsod64](https://gist.github.com/bsod64/c47c1251315d525793a9)
  - Torrent Download: inspired by [samukasmk](https://gist.github.com/samukasmk/940ca5d5abd9019e8b1af77c819e4ca9)
  - Extraction: i have written an extraction module to process the data specifically for personal purpose
  - Web-UI: i complicated the WebUI, so that the user can configure diffrent parameters
  - Download History: inspired by [nbr23](https://github.com/nbr23/youtube-dl-server)
  
  - Download:
    - wget
    - youtube-dl
    - torrent (magnetlink)

Planned:

  - 

---

### This Version supported following arguments for youtube-dl:

<pre><code>  - url
  - youtube-dl or wget o
  - download streams: normal (single) or axel (multiple download streams)
  - reference link
  - title
  - path (for subfolder)
  - retries (standard 5)
  - min sleep (standard 2)
  - max sleep (standard 15)
  - bandwidth (standard unlimited)
  - username
  - password
</code></pre>

![screenshot][1]

---

![screenshot][2]

---

![screenshot][3]

---

<!-- ### App Vars
<pre><code>  - custom Host: 'YDL_SERVER_HOST': '0.0.0.0'
  - custom Port: 'YDL_SERVER_PORT': 8080
  - simultaneous threads: 'WORKER_COUNT': 4
  - standard dir in /tmp/: 'DOWNLOAD_DIR': "ydl-downloads"
  - run local or as server/ docker, typ 'LOCAL'="." for local: 'LOCAL': "run"
  - download domain path: 'SUB_PATH': "downloads"
  - show hiddenfiles: 'SHOW_HIDDEN': False
</code></pre> -->

---

## Running

### Docker CLI

This example uses the docker run command to create the container to run the app. Here we also use host networking for simplicity. Also note the `-v` argument. This directory will be used to output the resulting videos

```shell
docker run -d -p 8080:8080 --name your-dl-server -v ./data/ydl-downloads:/tmp/ydl-downloads -v ./data/ydl-logs:/tmp/logs lramm/youtube-dl-server
```

### Docker Compose

This is an example service definition that could be put in `docker-compose.yml`. This service uses a VPN client container for its networking.

```yml
  youtube-dl:
    image: "lramm/your-dl-server"
    volumes:
      - ./data/ydl-logs:/tmp/logs
      - ./data/ydl-downloads:/tmp/ydl-downloads
    ports:
      - 8080:8080
    restart: always
```

### Podman CLI

Podman can be used like the Docker CLI.

```shell
podman run -d -p 8080:8080 --name your-dl-server -v ./data/ydl-downloads:/tmp/ydl-downloads:Z -v ./data/ydl-logs:/tmp/logs:Z lramm/youtube-dl-server
```

### K8S

An Example Config for Kubernetes is Provided in the k8s directory.

### Python

If you have python ^3.3.0 installed in your PATH you can simply run like this, providing optional environment variable overrides inline.

```shell
sudo YDL_SERVER_PORT=8123 python3 -u ./youtube-dl-server.py
```

## Usage

### Start a download remotely

Downloads can be triggered by supplying the `{{url}}` of the requested video through the Web UI or through the REST interface via curl, etc.

#### HTML

Just navigate to `http://{{host}}:8080/` and enter the requested `{{url}}`.

#### Curl

```shell
curl -X POST --data-urlencode "url={{url}}" http://{{host}}:8080/api/add
```

#### Fetch

```javascript
fetch(`http://${host}:8080/api/add`, {
  method: "POST",
  body: new URLSearchParams({
    url: url,
    format: "bestvideo"
  }),
});
```

#### Bookmarklet

Add the following bookmarklet to your bookmark bar so you can conviently send the current page url to your youtube-dl-server instance.

```javascript
javascript:!function(){fetch("http://${host}:8080/api/add",{body:new URLSearchParams({url:window.location.href,format:"bestvideo"}),method:"POST"})}();
```

### Downloading files

Simple Fileserver for Download or Streaming, navigate to http://hostip:port/downloads/

---
**NOTE**

Currently: Issue with Fileserver and Webpage, if you use both, it breaks after entering the Fileserver.

---

## Implementation

The server uses [`bottle`](https://github.com/bottlepy/bottle) for the web framework and [`youtube-dl`](https://github.com/rg3/youtube-dl) to handle the downloading.

This buildah image is based on [`python:3-alpine`](https://registry.hub.docker.com/_/python/).

[1]:docs/ui-download.png
[2]:docs/ui-fileserver.png
[3]:docs/ui-history.png