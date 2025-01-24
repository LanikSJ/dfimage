#!/usr/bin/env bash
# shellcheck disable=SC1091

set -e
source /app/bin/activate
python3 /app/dfimage.py "$1"
