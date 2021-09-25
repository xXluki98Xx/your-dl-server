#
# youtube-dl Server Dockerfile
#
# https://github.com/manbearwiz/youtube-dl-server-dockerfile
#

FROM python:alpine

# -----

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

# -----

RUN apk add --no-cache \
  ffmpeg \
  tzdata \
  axel

RUN pip install --no-cache-dir -r requirements.txt

# -----

COPY requirements.txt /usr/src/app/

EXPOSE 8080

CMD [ "python", "-u", "./youtube-dl-server.py" ]
