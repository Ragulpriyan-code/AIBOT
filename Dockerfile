FROM python:3.11-slim

# Prevent Python buffering & .pyc files
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Dummy key to avoid import crash during build
ENV GROQ_API_KEY="dummy_key_for_build_init"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files safely during build
RUN DATABASE_URL=sqlite:///dummy.db python manage.py collectstatic --noinput

# Copy & fix entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Railway injects PORT automatically
EXPOSE 8000

# Start app
CMD ["/app/entrypoint.sh"]
