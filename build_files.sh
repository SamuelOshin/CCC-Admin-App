#!/bin/bash

echo "BUILD START"
# Activate the virtual environment (correct path for Render)
source /opt/render/project/venv/bin/activate

# Install dependencies first
python3 -m pip install -r requirements.txt

# Run database migrations
python3 manage.py migrate

# Now run Django commands
python3 manage.py collectstatic --noinput --clear

echo "BUILD END"
