#!/bin/bash
set -e

# Print environment for debugging (excluding secrets)
echo "Starting application..."
echo "Current Directory: $(pwd)"
echo "User: $(whoami)"
echo "Python: $(python --version)"
echo "Variables: PORT=${PORT}"

# Defensive check for PORT
if [ -z "$PORT" ] || [ "$PORT" = '$PORT' ]; then
    echo "PORT is missing or invalid ('$PORT'). Defaulting to 8000."
    export PORT=8000
fi

# Run Gunicorn with config
exec gunicorn -c gunicorn_config.py chatbotapp.wsgi:application
