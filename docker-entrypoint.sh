#!/bin/bash

# Collect static files
echo "---Collect static files---"
python manage.py collectstatic --noinput

# Apply database migrations
echo "---Apply database migrations---"
python manage.py migrate

# Load example data for demonstration
echo "---Load initial data---"
python manage.py loaddata initial_data.json

# Start server
echo "---Starting server---"
./wait-for-it.sh db:5432 -- gunicorn django_project.wsgi -b 0.0.0.0:8000
