#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create database directory if it doesn't exist
mkdir -p /opt/render/project/src/

# Collect static files
python manage.py collectstatic --no-input

# Apply migrations
python manage.py migrate 