FROM python:3.11-slim

# Keep Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system requirements
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies (use cache mount to speed up installed)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files (dummy DB url to avoid connection errors during build)
RUN DATABASE_URL=sqlite:///dummy.db python manage.py collectstatic --noinput

# Run the application
CMD gunicorn chatbotapp.wsgi:application --bind 0.0.0.0:$PORT
