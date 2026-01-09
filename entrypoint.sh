#!/bin/sh
set -e

echo "PORT value is: $PORT"

exec gunicorn chatbotapp.wsgi:application \
  --config /dev/null \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --threads 4 \
  --timeout 120
