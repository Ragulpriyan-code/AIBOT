#!/bin/sh
set -e

# Default to 8000 if PORT is not set
PORT=${PORT:-8000}
echo "Starting server on port: $PORT"

exec gunicorn chatbotapp.wsgi:application \
  --config /dev/null \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
