#!/bin/sh

# Run database migrations
python manage.py migrate --no-input

# Collect all static files to the root directory
python manage.py collectstatic --no-input

# Start the gunicorn worker processes at the defined port
gunicorn cccadminapp.wsgi:application --bind 0.0.0.0:8000