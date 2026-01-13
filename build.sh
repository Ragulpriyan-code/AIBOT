#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python download_model.py
python manage.py collectstatic --no-input
python manage.py migrate
