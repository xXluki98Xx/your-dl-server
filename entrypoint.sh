#!/usr/bin/env bash
set -o errexit


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
