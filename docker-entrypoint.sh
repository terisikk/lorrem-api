#!/bin/sh

set -e

. /venv/bin/activate

exec gunicorn --bind 0.0.0.0:5000 wsgi:app --timeout 180
