#!/bin/bash

sed -i 's/\r$//' "$0"

echo "Running makemigrations"
python manage.py makemigrations
echo "Running migrations"
python manage.py migrate

echo "Running server"
python manage.py runserver 0.0.0.0:8000 &

echo "Run Celery worker in the background"
celery -A core worker --loglevel=info &

echo "Run Celery Beat in the background"
celery -A core beat --loglevel=info --scheduler django