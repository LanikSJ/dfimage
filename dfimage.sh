#!/usr/bin/env bash
# shellcheck disable=SC1091

set -e
python3 -m venv /app
source /app/bin/activate
pip install -e /app
yes | pip uninstall pip
python3 /app/dfimage.py "$1"
