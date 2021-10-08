FROM alpine/git AS git

RUN git clone --branch refactoring https://github.com/xXluki98Xx/your-dl-server.git /app/your-dl-server

# -----

FROM python:slim
MAINTAINER "lRamm <lukas.ramm.1998@gmail.com>"

# -----

COPY --from=git /app/your-dl-server/entrypoint.sh /app/your-dl-server/entrypoint.sh
COPY --from=git /app/your-dl-server/requirements.txt /app/your-dl-server/requirements.txt
COPY --from=git /app/your-dl-server/requirements-apt.txt /app/your-dl-server/requirements-apt.txt

COPY --from=git /app/your-dl-server/your-dl-server /app/your-dl-server/your-dl-server

RUN apt update && apt upgrade -y && \
    pip3 install --no-cache-dir -r /app/your-dl-server/requirements.txt --upgrade && cat /app/your-dl-server/requirements-apt.txt | xargs apt install -y && \
    rm -rf /var/lib/apt/lists/* /var/tmp/*

# -----

WORKDIR /app/your-dl-server

EXPOSE 8080

ENTRYPOINT [ "./entrypoint.sh" ]