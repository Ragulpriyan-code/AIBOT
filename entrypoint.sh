#!/bin/sh
set -e

# Default to 8000 if PORT is not set
PORT=${PORT:-8000}
echo "Starting server on port: $PORT"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Ensuring admin user exists..."
python manage.py shell << 'EOF'
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
exec gunicorn chatbotapp.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
