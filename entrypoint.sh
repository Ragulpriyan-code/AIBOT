#!/bin/sh
set -e

echo "Starting Gunicorn on port $PORT"

exec gunicorn chatbotapp.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --threads 4 \
  --timeout 120
