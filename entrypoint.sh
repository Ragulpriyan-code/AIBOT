#!/bin/sh
# Don't use 'set -e' - it causes premature exits on non-critical errors
# set -e

# Default to 8000 if PORT is not set
PORT=${PORT:-8000}
echo "Starting server on port: $PORT"

echo "Running database migrations..."
python manage.py migrate --noinput || {
    echo "⚠️ Migration failed, but continuing..."
}

echo "Collecting static files..."
# Create static directory if it doesn't exist
mkdir -p /app/static || true
python manage.py collectstatic --noinput || {
    echo "⚠️ Static collection failed, but continuing..."
}

echo "Ensuring admin user exists..."
python manage.py shell << 'EOF' || echo "⚠️ Admin user setup failed, but continuing..."
import os
from django.contrib.auth.models import User

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")
email = os.getenv("ADMIN_EMAIL", "")

if not username or not password:
    print("ADMIN_USERNAME or ADMIN_PASSWORD not set")
else:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print("Superuser created")
    else:
        print("Superuser already exists")
EOF

echo "🔄 Reloading documents into vector store..."
python manage.py reload_documents || echo "⚠️ Warning: Document reload failed, but continuing..."

echo "Starting Gunicorn..."
# Use sync workers for better stability (can switch to gthread later if needed)
# Add --preload to load app before forking workers (faster startup)
# Add --capture-output to capture print statements
exec gunicorn chatbotapp.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --worker-class sync \
  --threads 4 \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --preload \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  --capture-output
