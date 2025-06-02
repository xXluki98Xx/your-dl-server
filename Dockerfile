FROM docker.io/python:3.12.7-slim-bookworm AS build-pip

COPY ./ /app
RUN cd /app \
  && ls -la \
  && pip install build \
  && python -m build

# -----

FROM docker.io/python:3.12.7-slim-bookworm
LABEL org.opencontainers.image.authors="lRamm <lramm.dev@gmail.com>"
ENV TZ=Europe/Berlin

ARG WORKPATH=/app


COPY ./requirements.* $WORKPATH/
RUN apt-get update && apt-get upgrade -y \
  && cat $WORKPATH/requirements.apt | xargs apt-get install -y --no-install-recommends \
  && rm $WORKPATH/requirements.* \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata \
  && rm -rf /var/lib/apt/lists/* /var/tmp/*


COPY --from=build-pip /app/dist/* $WORKPATH/
RUN cd $WORKPATH \
  && ls -la \
  && pip install *.gz \
  && rm -r $WORKPATH/* \
  && ls -la

# -----

COPY torrc $WORKPATH/
RUN apt-get update \
  && apt-get install -y tor \
  && sed "1s/^/SocksPort 0.0.0.0:9050\n/" /$WORKPATH/torrc > /etc/tor/torrc \
  && rm /$WORKPATH/torrc \
  && rm -rf /var/lib/apt/lists/* /var/tmp/*

# -----

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

WORKDIR $WORKPATH
EXPOSE 8080

CMD [ "server" ]
ENTRYPOINT [ "/entrypoint.sh" ]
