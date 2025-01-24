#!/usr/bin/env bash
# shellcheck disable=SC1091

set -e
python3 -m venv /app
source /app/bin/activate
for i in $(pip list --outdated --format=json |jq -r '.[].name' ) ; do pip install -U $i; done
pip install -e /app
yes | pip uninstall pip
python3 /app/dfimage.py "$1"
