#!/usr/bin/env bash
set -e
# shellcheck disable=SC1091
source /app/bin/activate
python3 /app/entrypoint.py "$1"
