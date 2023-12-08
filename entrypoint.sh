#!/usr/bin/env bash
set -e
# shellcheck disable=SC1091
source /root/.local/share/pipx/venvs/cookiecutter/bin/activate
python3 /root/entrypoint.py $1