FROM docker.io/python:slim AS build

COPY ./ /app

RUN cd /app \
    && pip install build \
    && python -m build

# -----

FROM docker.io/python:slim
MAINTAINER "lRamm <lukas.ramm.1998@gmail.com>"


COPY ./*requirements /app/
COPY entrypoint.sh /

RUN apt-get update && apt-get upgrade -y \
    && pip3 install --no-cache-dir -r /app/pip.requirements --upgrade \
    && cat /app/apt.requirements | xargs apt-get install -y \ 
    && rm -rf /var/lib/apt/lists/* /var/tmp/*


COPY --from=build /app/dist/* /app/

RUN cd /app \
    && ls -la \
    && pip install *.gz

# -----

WORKDIR /srv

EXPOSE 8080

CMD [ "server" ]
ENTRYPOINT [ "/entrypoint.sh" ]
