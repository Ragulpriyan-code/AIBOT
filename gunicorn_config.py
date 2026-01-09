import os

# Gunicorn configuration
# Read the PORT environment variable, defaulting to 8000
port = os.environ.get("PORT", "8000")
# Defensive check: If PORT is literally "$PORT" or not a digit, fallback to 8000
if not port.isdigit() and port.startswith("$"):
    port = "8000"
bind = f"0.0.0.0:{port}"

# Worker configuration
workers = 2
threads = 4
worker_class = "gthread"

# Timeout
timeout = 120

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
