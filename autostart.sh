#!/bin/bash

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Collect movie and planet data
python manage.py load_data

# Start the Django development server
python manage.py runserver 0.0.0.0:8000