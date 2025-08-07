#!/bin/sh

echo "Running migrations..."
python nfa/manage.py migrate

echo "Starting server..."
python nfa/manage.py runserver 0.0.0.0:8080