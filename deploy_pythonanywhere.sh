#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/Bamaham93/FS2020"
VENV="/home/Bamaham93/.virtualenvs/hbc-env"
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"

SHA="${1:-}"

cd "$APP_DIR"

git fetch origin

if [[ -n "$SHA" ]]; then
  git reset --hard "$SHA"
else
  git reset --hard origin/master
fi

$PIP install -r requirements.txt

$PY python_anywhere_website/manage.py migrate --noinput
$PY python_anywhere_website/manage.py collectstatic --noinput
