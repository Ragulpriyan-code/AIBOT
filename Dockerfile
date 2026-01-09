FROM python:3.11-slim

# Keep Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# PREVENT CRASH: Set dummy keys so app imports don't fail at startup
# (Real keys must still be provided in Railway variables for functionality)
ENV GROQ_API_KEY="dummy_key_for_build_init"

# Install system requirements
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files (uses dummy DB to avoid build-time connection errors)
RUN DATABASE_URL=sqlite:///dummy.db python manage.py collectstatic --noinput

# Run the application
CMD ["gunicorn", "-c", "gunicorn_config.py", "chatbotapp.wsgi:application"]
