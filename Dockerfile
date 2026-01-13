FROM python:3.10-slim

# Prevent Python buffering & .pyc files
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Dummy key to avoid import crash during build
ENV GROQ_API_KEY="dummy_key_for_build_init"

# Install system dependencies
# - build-essential: Required for compiling Python packages
# - libpq-dev: PostgreSQL client library for psycopg2
# - libopenblas-dev: Required for faiss-cpu numerical operations
# - libomp-dev: OpenMP library for faiss-cpu parallel processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy & fix entrypoint (line endings and permissions)
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# EXPOSE is just documentation - actual port comes from $PORT env var
EXPOSE 8000

# Use shell form CMD so $PORT environment variable is expanded correctly
# JSON array form ["/app/entrypoint.sh"] prevents shell variable expansion
# This is critical for Render which injects $PORT at runtime
CMD /app/entrypoint.sh
