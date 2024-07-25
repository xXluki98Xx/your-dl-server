#!/usr/bin/env bash
set -o errexit

# generate a random secret
export SECRET=$(openssl rand -hex 32)
export TOR_SECRET=$(tor --hash-password $SECRET | sed -n 's/^.*16:/16:/p')


sed -i "1s/^/ControlPort 9051\n/" /etc/tor/torrc
sed -i "1s/^/HashedControlPassword $TOR_SECRET\n/" /etc/tor/torrc
sed -i "1s/^/RunAsDaemon 1\n/" /etc/tor/torrc


# how should commands be handled
case "$1" in
    sh|bash)
        echo "got extra command: $@"
        set -- "$@"
    ;;
    *)
        set -- dl "$@"
    ;;
esac

echo "---"
echo "running: $@"
exec "$@"
