FROM docker.io/python:slim AS build-ydl

COPY ./ /app

RUN cd /app \
    && pip install build \
    && python -m build

# -----

FROM docker.io/python:slim
MAINTAINER "lRamm <lukas.ramm.1998@gmail.com>"

ARG WORKPATH=/app


COPY ./requirements.* $WORKPATH/

RUN apt-get update && apt-get upgrade -y \
    && pip3 install --no-cache-dir -r $WORKPATH/requirements.pip --upgrade \
    && cat $WORKPATH/requirements.apt | xargs apt-get install -y \
    && rm $WORKPATH/requirements.* \
    && rm -rf /var/lib/apt/lists/* /var/tmp/*


COPY --from=build-ydl /app/dist/* $WORKPATH/

RUN cd $WORKPATH \
    && ls -la \
    && pip install *.gz \
    && rm -r $WORKPATH/* \
    && ls -la

# -----

COPY torrc /$WORKPATH/

RUN apt-get update \
    && apt-get install -y tor \
    && sed "1s/^/SocksPort 0.0.0.0:9050\n/" /$WORKPATH/torrc > /etc/tor/torrc \
    && rm /$WORKPATH/torrc \
    && rm -rf /var/lib/apt/lists/* /var/tmp/*

# -----

COPY entrypoint.sh /

WORKDIR $WORKPATH

EXPOSE 8080

CMD [ "server" ]
ENTRYPOINT [ "/entrypoint.sh" ]
