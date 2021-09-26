FROM debian:stable-slim

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

ENTRYPOINT [ "/entrypoint.sh", "server" ]

CMD [ "python", "-u", "./youtube-dl-server.py" ]
