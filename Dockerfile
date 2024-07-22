FROM docker.io/python:slim AS build

COPY ./ /app

RUN cd /app \
    && pip install build \
    && python -m build

# -----

FROM docker.io/python:slim
MAINTAINER "lRamm <lukas.ramm.1998@gmail.com>"

ARG WORKPATH=/app


COPY ./*requirements $WORKPATH/
COPY entrypoint.sh /

RUN apt-get update && apt-get upgrade -y \
    && pip3 install --no-cache-dir -r $WORKPATH/pip.requirements --upgrade \
    && cat $WORKPATH/apt.requirements | xargs apt-get install -y \
    && rm $WORKPATH/*requirements \
    && rm -rf /var/lib/apt/lists/* /var/tmp/*


COPY --from=build /app/dist/* $WORKPATH/

RUN cd $WORKPATH \
    && ls -la \
    && pip install *.gz \
    && rm -r $WORKPATH/* \
    && ls -la

# -----

WORKDIR $WORKPATH

EXPOSE 8080

CMD [ "server" ]
ENTRYPOINT [ "/entrypoint.sh" ]
