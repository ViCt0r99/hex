#!/bin/bash
echo "Starting Migrations..."
python src/manage.py migrate
echo ====================================

# collect static files
echo "Collecting Static files..."
python3 src/manage.py collectstatic --noinput

echo "Starting Server..."
python src/manage.py runserver 0.0.0.0:8000