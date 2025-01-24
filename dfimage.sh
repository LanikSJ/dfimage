#!/usr/bin/env bash
# shellcheck disable=SC1091

set -e
python3 -m venv .
source ./bin/activate
pip install -e .
yes | pip uninstall pip
python3 ./dfimage.py "$1"
