#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Download model to local cache during BUILD phase
python download_model.py

# Collect static files during BUILD phase
python manage.py collectstatic --no-input
